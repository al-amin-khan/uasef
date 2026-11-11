"""Durable history, model handoffs and real Git checkpoint isolation."""
from concurrent.futures import ThreadPoolExecutor
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from uasef import cli, executor, memory as m, orchestrator as o, sessions


class MemoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p = Path(tmp.name) / "product"
        self.call("init", str(self.p), "--idea", "Track changing inventory requirements")

    def call(self, *args, expected=0):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(args))
        self.assertEqual(code, expected, out.getvalue())
        return out.getvalue()

    def task(self):
        with o.db(self.p) as conn:
            return o.add_task(conn, self.p, "API-001", "Inventory API", "backend-engineer",
                              "feature-implementation", "Verify inventory reconciliation")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.p), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_initial_idea_idempotent_sync_and_upgrade_preserve_history(self):
        before = {r["id"]: r for r in m.records(self.p)}
        self.assertEqual(len([r for r in before.values() if r["kind"] == "idea"]), 1)
        self.assertIn("Track changing inventory", m.brief(self.p))
        m.sync(self.p)
        self.assertEqual(before, {r["id"]: r for r in m.records(self.p)})
        charter = self.p / "AGENTS.md"
        charter.write_text("Custom owner instructions", encoding="utf-8")
        self.call("upgrade", "--project", str(self.p))
        self.assertEqual(charter.read_text(), "Custom owner instructions")
        for identifier, row in before.items():
            self.assertEqual(row, next(r for r in m.records(self.p) if r["id"] == identifier))

    def test_long_original_idea_and_migration_from_pre_memory_project(self):
        idea = "Inventory requirements " * 1200
        target = self.p.parent / "long-project"
        self.call("init", str(target), "--idea", idea)
        parts = [r for r in m.records(target) if r["kind"] == "idea"]
        self.assertEqual(len(parts), 3)
        # Chunks preserve substantive text; boundary whitespace is normalized.
        self.assertEqual("".join(r["text"] for r in parts).replace(" ", ""), idea.replace(" ", ""))
        before = cli.load(self.p)
        before["framework_version"] = "0.3.0"
        m.directory(self.p).rename(self.p.parent / "earlier-memory")
        cli.save(self.p, before)
        charter = (self.p / "AGENTS.md").read_bytes()
        self.call("upgrade", "--project", str(self.p))
        self.assertEqual((self.p / "AGENTS.md").read_bytes(), charter)
        self.assertEqual(cli.load(self.p)["tasks"], before["tasks"])
        self.assertIn("Track changing inventory", m.brief(self.p))

    def test_links_replacements_evidence_and_claims(self):
        self.task()
        req = m.add(self.p, "requirement", "Latency", "Changes must appear within five seconds")
        choice = m.add(self.p, "decision", "Queue", "Use a queue because bursts exceed synchronous capacity; alternative: polling",
                       links=[req["id"]], task="API-001")
        changed = m.add(self.p, "decision", "Batch queue", "Batch writes after measured disk contention",
                        supersedes=choice["id"], links=[req["id"]], task="API-001")
        evidence = self.p / "docs" / "test-result.md"
        evidence.write_text("Measured latency: four seconds", encoding="utf-8")
        proof = m.add(self.p, "verification", "Latency check", "Measured four seconds; operator report",
                      links=[changed["id"]], task="API-001", evidence=["docs/test-result.md"])
        self.assertEqual(proof["evidence"][0]["sha256"], hashlib.sha256(evidence.read_bytes()).hexdigest())
        self.assertEqual(m.validate(self.p), [])
        evidence.write_text("Different result", encoding="utf-8")
        self.assertIn("evidence changed", "\n".join(m.validate(self.p)))
        ids = {r["id"] for r in m.trace(self.p, req["id"])}
        self.assertTrue({req["id"], choice["id"], changed["id"], proof["id"]} <= ids)
        brief = m.brief(self.p, "API-001")
        self.assertIn("Batch writes after", brief)
        self.assertNotIn("Use a queue because", brief)
        pref = m.add(self.p, "preference", "Possible preference", "Prefers smaller changes", actor="model-A", claim="inferred")
        self.assertIn("inferred", m.brief(self.p))
        confirmation = m.add(self.p, "preference", "Confirmed preference", "Keep changes small", actor="owner",
                             claim="confirmed", supersedes=pref["id"])
        self.assertEqual(confirmation["claim"], "confirmed")
        self.assertEqual(choice, next(r for r in m.records(self.p) if r["id"] == choice["id"]))

    def test_invalid_links_evidence_and_commits_fail_without_records(self):
        count = len(m.records(self.p))
        for extra in ({"links": ["MEM-" + "0" * 32]}, {"task": "MISSING-001"},
                      {"evidence": ["../outside"]}, {"evidence": [".env"]}, {"commit": "--all"}):
            with self.assertRaises(ValueError):
                m.add(self.p, "decision", "Invalid", "Must not be recorded", **extra)
        self.assertEqual(count, len(m.records(self.p)))

    def test_model_prompt_and_both_handoffs_include_memory(self):
        task = self.task()
        m.add(self.p, "decision", "Storage", "Retain SQL because the team supports it", task=task["id"])
        self.assertIn("Retain SQL", executor.build_prompt(self.p, task))
        self.call("handoff", "--project", str(self.p))
        self.assertIn("Retain SQL", (self.p / ".uasef/handoff.md").read_text())
        with o.db(self.p) as conn:
            session = sessions.start(conn, task["id"], "Switch to model B")
            sessions.record(conn, self.p, session["id"], "checkpoint", "model-A", "Next: test the query")
            dest = sessions.export(conn, self.p, session["id"])
        self.assertIn("Retain SQL", dest.read_text())
        self.assertTrue(any(r["text"] == "Next: test the query" for r in m.trace(self.p, "API-001")))

    def test_automatic_task_history_retry_and_no_duplicate_sync(self):
        self.task()
        with o.db(self.p) as conn:
            run, token = o.claim(conn, "API-001", "mock")
        with o.db(self.p) as conn:
            o.finish_run(conn, "API-001", run, token, 1, self.p / "prompt", self.p / "log", self.p, "failed")
        with o.db(self.p) as conn:
            o.retry(conn, "API-001", "operator")
        trail = m.trace(self.p, "API-001")
        self.assertEqual([r for r in trail if r["kind"] == "task"][-1]["data"]["status"], "queued")
        self.assertTrue(any(r["title"] == "run_finished" for r in trail))
        before = m.records(self.p)
        m.sync(self.p)
        self.assertEqual(before, m.records(self.p))

    def test_parallel_records_survive(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(lambda i: m.add(self.p, "finding", f"Finding {i}", f"Observed result {i}"), range(8)))
        ids = {r["id"] for r in m.records(self.p)}
        self.assertEqual(len({r["id"] for r in rows}), 8)
        self.assertTrue(all(r["id"] in ids for r in rows))

    def test_cli_commands_and_brief_budget(self):
        identifier = self.call("memory", "add", "brief", "--title", "Current work", "--text", "Next: clarify user acceptance",
                               "--project", str(self.p)).strip()
        self.assertIn("Next: clarify", self.call("memory", "brief", "--project", str(self.p)))
        self.assertIn(identifier, self.call("memory", "show", identifier, "--project", str(self.p)))
        self.assertIn(identifier, self.call("memory", "trace", identifier, "--project", str(self.p)))
        self.assertIn(identifier, self.call("memory", "list", "--kind", "brief", "--search", "acceptance", "--project", str(self.p)))
        for i in range(20):
            m.add(self.p, "finding", f"Large {i}", "x" * 12000)
        self.assertLess(len(m.brief(self.p)), 22000)
        self.call("memory", "brief", "--limit", "0", "--project", str(self.p), expected=2)

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_checkpoint_preserves_unrelated_staging_and_trace_survives_clone(self):
        self.git("init")
        self.git("config", "user.name", "Memory Test")
        self.git("config", "user.email", "memory@example.invalid")
        unrelated = self.p / "unrelated.txt"
        unrelated.write_text("Already staged work")
        self.git("add", "unrelated.txt")
        head = m.checkpoint(self.p, "docs: capture original idea")
        files = self.git("show", "--pretty=", "--name-only", "HEAD").splitlines()
        self.assertTrue(all(f.startswith("docs/project-memory/") for f in files if f))
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.txt")
        self.assertEqual(m.checkpoint(self.p, "docs: no changes"), "No memory changes to commit")
        task = self.task()
        record = m.add(self.p, "decision", "History", "Preserve this rationale", task=task["id"], commit=head)
        m.checkpoint(self.p, "docs: record task decision")
        # Copy the committed memory into a fresh initialized project without runtime SQLite.
        clone = self.p.parent / "fresh"
        shutil.copytree(m.directory(self.p), m.directory(clone), dirs_exist_ok=True)
        self.assertIn(record["id"], {r["id"] for r in m.trace(clone, task["id"])})
        self.assertIn("Preserve this rationale", self.call("memory", "brief", "--project", str(clone)))


if __name__ == "__main__":
    unittest.main()

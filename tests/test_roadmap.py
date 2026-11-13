import contextlib
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile

from uasef import backup, cli, memory as m, memory_query as query, orchestrator as o, sessions, verification as v


class RoadmapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.p = self.root / "project"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["init", str(self.p), "--idea", "Reliable project history"]), 0)

    def task(self):
        with o.db(self.p) as conn:
            return o.add_task(conn, self.p, "API-001", "API", "backend-engineer", "feature-implementation", "Check behavior")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.p), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self):
        self.git("init")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("add", ".")
        self.git("commit", "-m", "test: initial state")

    def test_backup_roundtrip_sessions_and_upgrade(self):
        self.task()
        with o.db(self.p) as conn:
            session = sessions.start(conn, "API-001", "Design session")
            sessions.record(conn, self.p, session["id"], "checkpoint", "owner", "Resume with API tests")
        archive = self.root / "state.zip"
        backup.create(self.p, archive)
        restored = self.root / "restored"
        backup.restore(archive, restored)
        self.assertEqual(cli.load(restored), cli.load(self.p))
        self.assertEqual(m.records(restored), m.records(self.p))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["upgrade", "--project", str(restored)]), 0)
        with o.db(restored) as conn:
            self.assertEqual(o.task(conn, "API-001")["status"], "queued")
            self.assertIn("Resume with API tests", sessions.context(conn, session["id"]))
        self.assertTrue((restored / ".uasef/roles/backend-engineer.md").exists())

    def test_backup_refuses_running_task_and_existing_destination(self):
        self.task()
        with o.db(self.p) as conn:
            o.claim(conn, "API-001", "worker")
        with self.assertRaises(ValueError):
            backup.create(self.p, self.root / "busy.zip")
        with self.assertRaises(ValueError):
            backup.restore(self.root / "irrelevant.zip", self.p)

    def test_malicious_archive_and_checksum_fail_without_destination(self):
        archive = self.root / "state.zip"
        backup.create(self.p, archive)
        with zipfile.ZipFile(archive, "a") as z:
            z.writestr("../escape.txt", "bad")
        target = self.root / "restored"
        with self.assertRaises(ValueError):
            backup.restore(archive, target)
        self.assertFalse(target.exists())
        self.assertFalse((self.root / "escape.txt").exists())
        good = self.root / "good.zip"
        backup.create(self.p, good)
        damaged = self.root / "damaged.zip"
        with zipfile.ZipFile(good) as source, zipfile.ZipFile(damaged, "w") as z:
            for name in source.namelist():
                z.writestr(name, b"{}" if name.endswith("state.json") else source.read(name))
        with self.assertRaises(ValueError):
            backup.restore(damaged, target)
        self.assertFalse(target.exists())

    def test_migrate_old_database_parent_column_and_preserve_history(self):
        self.task()
        path = o.database_path(self.p)
        with contextlib.closing(sqlite3.connect(path)) as conn:
            conn.execute("ALTER TABLE tasks DROP COLUMN parent_id")
            conn.commit()
        with o.db(self.p) as conn:
            self.assertIsNone(o.task(conn, "API-001")["parent_id"])
            self.assertEqual(len(o.list_tasks(conn)), 1)
        with o.db(self.p) as conn:
            self.assertEqual(len(o.list_tasks(conn)), 1)

    def test_recovery_rejects_stale_worker_and_can_retry(self):
        self.task()
        with o.db(self.p) as conn:
            run, token = o.claim(conn, "API-001", "worker")
            conn.execute("UPDATE tasks SET lease_until='2000-01-01T00:00:00+00:00' WHERE id='API-001'")
            self.assertEqual(o.recover_expired(conn), ["API-001"])
            self.assertEqual(o.recover_expired(conn), [])
            with self.assertRaises(ValueError):
                o.finish_run(conn, "API-001", run, token, 0, "prompt", "log", self.p, "")
            o.retry(conn, "API-001", "owner")
            _, fresh = o.claim(conn, "API-001", "worker2")
            self.assertNotEqual(token, fresh)

    def test_abrupt_worker_exit_preserves_claim_for_recovery(self):
        self.task()
        result = subprocess.run([sys.executable, "-c",
            "import os,sys; from uasef import orchestrator as o; "
            "ctx=o.db(sys.argv[1]); c=ctx.__enter__(); o.claim(c,'API-001','crashed',lease_seconds=-1); os._exit(9)", str(self.p)])
        self.assertEqual(result.returncode, 9)
        with o.db(self.p) as conn:
            self.assertEqual(o.recover_expired(conn), ["API-001"])
            self.assertEqual(conn.execute("SELECT status FROM runs").fetchone()[0], "interrupted")

    def test_supported_inception_migrations(self):
        for version in ("0.1.0", "0.2.0", "0.3.0", "0.4.0"):
            state = cli.load(self.p)
            state["framework_version"] = version
            cli.write_json(self.p / ".uasef/state.json", state)
            before = state["tasks"]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["upgrade", "--project", str(self.p)]), 0)
            self.assertEqual(cli.load(self.p)["tasks"], before)

    def test_verification_actual_command_and_staleness(self):
        self.commit()
        row = v.execute(self.p, [sys.executable, "-c", "assert 2 + 2 == 4"])
        self.assertTrue(row["passed"])
        v.require_current(self.p, row["id"])
        (self.p / "changed.txt").write_text("changed")
        with self.assertRaises(ValueError):
            v.require_current(self.p, row["id"])
        self.git("add", "changed.txt")
        self.git("commit", "-m", "feat: changed source")
        with self.assertRaises(ValueError):
            v.require_current(self.p, row["id"])
        failed = v.execute(self.p, [sys.executable, "-c", "raise SystemExit(3)"])
        self.assertFalse(failed["passed"])

    def test_verification_detects_command_mutation(self):
        self.commit()
        row = v.execute(self.p, [sys.executable, "-c", "from pathlib import Path; Path('new.txt').write_text('changed')"])
        self.assertFalse(row["passed"])
        self.assertFalse(row["unchanged"])

    def test_required_gate_cannot_be_omitted(self):
        (self.p / ".uasef/verification-policy.json").write_text('{"required":true}')
        with self.assertRaises(ValueError):
            v.gate(self.p)

    def test_task_review_enforces_current_receipt(self):
        self.task()
        evidence = self.p / "docs/review.md"
        evidence.write_text("Acceptance checked independently")
        with o.db(self.p) as conn:
            o.submit_manual(conn, self.p, "API-001", "developer", ["docs/review.md"])
        (self.p / ".uasef/verification-policy.json").write_text('{"required":true}')
        self.commit()
        receipt = v.execute(self.p, [sys.executable, "-c", "assert True"])
        with o.db(self.p) as conn:
            with self.assertRaises(ValueError):
                o.verify(conn, self.p, "API-001", "reviewer", ["docs/review.md"])
            self.assertEqual(o.verify(conn, self.p, "API-001", "reviewer", ["docs/review.md"], receipt["id"]), "completed")

    def test_index_updates_deletes_and_timeline_conflicts(self):
        first = m.add(self.p, "decision", "Storage", "Use SQLite for local operation")
        second = m.add(self.p, "decision", "Storage", "Use PostgreSQL for distributed operation", supersedes=first["id"])
        third = m.add(self.p, "decision", "Storage", "Use files for portable operation", supersedes=first["id"])
        self.assertEqual(query.search(self.p, "PostgreSQL")[0]["id"], second["id"])
        self.assertTrue(any(i["kind"] == "competing_revisions" for i in query.conflicts(self.p)))
        self.assertFalse(next(r for r in query.timeline(self.p) if r["id"] == first["id"])["current"])
        path = m.directory(self.p) / "records" / (second["id"] + ".json")
        row = json.loads(path.read_text()); row["text"] = "Use MariaDB instead"
        path.write_text(json.dumps(row))
        self.assertEqual(query.search(self.p, "PostgreSQL"), [])
        self.assertEqual(query.search(self.p, "MariaDB")[0]["id"], second["id"])
        path.unlink()
        self.assertEqual(query.search(self.p, "MariaDB"), [])
        self.assertEqual(len(query.search(self.p, "operation", limit=1)), 1)

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from uasef import cli, orchestrator as o, executor
from readiness_fixture import approved_inception


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / "project"
        self.assertEqual(self.call("init", str(self.p)), 0)
        (self.p / "evidence.md").write_text("Observed experiment results " * 10)

    def call(self, *args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            result = cli.main(list(args))
        self.output = stream.getvalue()
        return result

    def add(self, **kwargs):
        with o.db(self.p) as conn:
            return o.add_task(conn, self.p, "WORK-001", "Scoped work", "backend-engineer",
                              "feature-implementation", "Check observable behavior", **kwargs)

    def test_pending_blocks_claim_preview_and_manual_without_attempt(self):
        self.add()
        self.assertEqual(self.call("dispatch", "WORK-001", "--project", str(self.p)), 2)
        self.assertIn("INIT-001", self.output)
        self.assertEqual(self.call("dispatch-ready", "--project", str(self.p)), 2)
        self.assertIn("INIT-001", self.output)
        with o.db(self.p) as conn:
            self.assertEqual(o.ready_tasks(conn), [])
            with self.assertRaisesRegex(ValueError, "INIT-001"):
                o.claim(conn, "WORK-001", "test")
            with self.assertRaisesRegex(ValueError, "INIT-001"):
                o.submit_manual(conn, self.p, "WORK-001", "author", ["evidence.md"])
            self.assertEqual(o.task(conn, "WORK-001")["attempts"], 0)
            self.assertEqual(conn.execute("SELECT count(*) FROM runs").fetchone()[0], 0)

    def test_real_inception_transitions_unlock_and_artifact_removal_blocks(self):
        self.add()
        state = cli.load(self.p)
        for item in state["tasks"]:
            for rel in item["outputs"]:
                (self.p / rel).write_text("Documented decisions, risks and acceptance evidence. " * 5)
            self.assertEqual(self.call("start", item["id"], "--project", str(self.p)), 0, self.output)
            self.assertEqual(self.call("complete", item["id"], "--project", str(self.p)), 0, self.output)
            if item["approval_required"]:
                self.assertEqual(self.call("approve", item["id"], "--project", str(self.p),
                                          "--note", "Owner reviewed and accepted scoped inception"), 0, self.output)
        with o.db(self.p) as conn:
            self.assertTrue(o.eligible(conn, o.task(conn, "WORK-001")))
            (self.p / "docs/00-inception/readiness-review.md").unlink()
            with self.assertRaisesRegex(ValueError, "artifacts"):
                o.claim(conn, "WORK-001", "test")

    def test_missing_approval_and_corrupt_state_fail_closed(self):
        self.add()
        approved_inception(self.p)
        state = cli.load(self.p)
        state["tasks"][-1].pop("approval_note")
        cli.write_json(cli.state_path(self.p), state)
        with o.db(self.p) as conn:
            self.assertFalse(o.eligible(conn, o.task(conn, "WORK-001")))
        cli.state_path(self.p).write_text("{")
        with o.db(self.p) as conn:
            with self.assertRaisesRegex(ValueError, "Invalid inception"):
                o.claim(conn, "WORK-001", "test")

    def test_planning_step_matches_role_and_dependencies(self):
        with o.db(self.p) as conn:
            t = o.add_task(conn, self.p, "PLAN-001", "Idea research", "product-manager",
                           "project-inception", "Produce idea brief", inception_step="INIT-001")
            self.assertTrue(o.eligible(conn, t))
            with self.assertRaisesRegex(ValueError, "role"):
                self.add(inception_step="INIT-001")
            with self.assertRaisesRegex(ValueError, "incomplete"):
                o.add_task(conn, self.p, "PLAN-002", "Discover requirements", "business-analyst",
                           "requirements-discovery", "Produce requirements", inception_step="INIT-002")
            o.submit_manual(conn, self.p, "PLAN-001", "researcher", ["evidence.md"])
        self.assertEqual(cli.load(self.p)["tasks"][0]["status"], "pending")

    def test_spike_is_recorded_prompted_and_one_attempt(self):
        t = self.add(spike_reason="Measure whether the API is feasible",
                     spike_scope="Disposable local prototype; no production writes", spike_hours=1)
        self.assertIn("Disposable local prototype", executor.build_prompt(self.p, t))
        with o.db(self.p) as conn:
            run, token = o.claim(conn, "WORK-001", "test")
            o.finish_run(conn, "WORK-001", run, token, 7, "prompt", "log", str(self.p))
            o.retry(conn, "WORK-001", "operator")
            with self.assertRaisesRegex(ValueError, "one attempt"):
                o.claim(conn, "WORK-001", "test")
            self.assertTrue(conn.execute("SELECT 1 FROM audit WHERE event='readiness_scope'").fetchone())

    def test_spike_expiry_invalid_fields_and_no_delegated_inheritance(self):
        with self.assertRaises(ValueError):
            self.add(spike_reason="short", spike_scope="Bounded local experiment only")
        self.add(spike_reason="Investigate API feasibility locally", spike_scope="Local isolated experiment only")
        with o.db(self.p) as conn:
            child = o.add_task(conn, self.p, "CHILD-001", "Child", "backend-engineer",
                               "feature-implementation", "Check results", parent_id="WORK-001")
            self.assertFalse(o.eligible(conn, child))
            policy = json.loads(o.task(conn, "WORK-001")["readiness_scope"])
            policy["expires_at"] = "2000-01-01T00:00:00+00:00"
            conn.execute("UPDATE tasks SET readiness_scope=? WHERE id='WORK-001'", (json.dumps(policy),))
            with self.assertRaisesRegex(ValueError, "expired"):
                o.submit_manual(conn, self.p, "WORK-001", "author", ["evidence.md"])

    def test_legacy_tasks_migrate_to_implementation_gate(self):
        self.add()
        with o.db(self.p) as conn:
            conn.execute("ALTER TABLE tasks DROP COLUMN readiness_scope")
        with o.db(self.p) as conn:
            self.assertEqual(json.loads(o.task(conn, "WORK-001")["readiness_scope"])["kind"], "implementation")
            self.assertFalse(o.eligible(conn, o.task(conn, "WORK-001")))

    def test_manual_spike_consumes_attempt(self):
        self.add(spike_reason="Investigate API feasibility locally", spike_scope="Local isolated experiment only")
        with o.db(self.p) as conn:
            o.submit_manual(conn, self.p, "WORK-001", "author", ["evidence.md"])
            self.assertEqual(o.task(conn, "WORK-001")["attempts"], 1)

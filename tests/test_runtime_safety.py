import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from uasef import cli, executor, orchestrator as o
from readiness_fixture import approved_inception


class RuntimeSafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / "project"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["init", str(self.p)]), 0)
        approved_inception(self.p)
        self.prompt = self.p / "prompt.txt"
        self.prompt.write_text("Bounded test input")
        self.log = self.p / "runner.log"

    def execute(self, script, **settings):
        profile = {"type": "subprocess", "argv": [sys.executable, "-c", script], "timeout_seconds": 10}
        profile.update(settings)
        return executor.execute(self.p, "test", profile, self.prompt, self.log, self.p, "WORK-001")

    def add(self, max_attempts=3):
        with o.db(self.p) as conn:
            o.add_task(conn, self.p, "WORK-001", "Scoped test", "backend-engineer",
                       "feature-implementation", "Check behavior", max_attempts=max_attempts)

    def test_timeout_stops_descendant_and_prevents_late_write(self):
        marker = self.p / "late.txt"
        child = "import time,pathlib; time.sleep(3); pathlib.Path(" + repr(str(marker)) + ").write_text('orphan')"
        script = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); time.sleep(30)"
        code, error = self.execute(script, timeout_seconds=1)
        self.assertEqual(code, 124, error)
        time.sleep(3.2)
        self.assertFalse(marker.exists(), "Descendant survived timeout")

    def test_normal_parent_exit_also_cleans_descendant(self):
        marker = self.p / "late.txt"
        child = "import time,pathlib; time.sleep(2); pathlib.Path(" + repr(str(marker)) + ").write_text('orphan')"
        script = "import subprocess,sys; subprocess.Popen([sys.executable,'-c'," + repr(child) + "])"
        code, error = self.execute(script)
        self.assertEqual(code, 0, error)
        time.sleep(2.2)
        self.assertFalse(marker.exists())

    def test_output_is_bounded_and_excess_fails(self):
        code, error = self.execute("import sys; sys.stdout.buffer.write(b'x'*2000000); sys.stdout.flush()", max_output_bytes=4096)
        self.assertEqual(code, 125, error)
        self.assertLessEqual(self.log.stat().st_size, 4096)

    def test_environment_requires_explicit_allowlist(self):
        with patch.dict(os.environ, {"UASEF_TEST_SECRET": "test-value-only"}):
            script = "import os; print(os.environ.get('UASEF_TEST_SECRET','absent'))"
            self.assertEqual(self.execute(script)[0], 0)
            self.assertEqual(self.log.read_text().strip(), "absent")
            self.assertEqual(self.execute(script, env_allowlist=["UASEF_TEST_SECRET"])[0], 0)
            self.assertEqual(self.log.read_text().strip(), "test-value-only")

    def test_attempt_limit_blocks_retry_and_claim(self):
        self.add(max_attempts=2)
        with o.db(self.p) as conn:
            for attempt in range(2):
                run, token = o.claim(conn, "WORK-001", "test")
                o.finish_run(conn, "WORK-001", run, token, 7, "prompt", "log", str(self.p))
                if attempt == 0:
                    o.retry(conn, "WORK-001", "operator")
            with self.assertRaisesRegex(ValueError, "attempt limit"):
                o.retry(conn, "WORK-001", "operator")
            self.assertEqual(o.task(conn, "WORK-001")["attempts"], 2)

    def test_cancel_running_worker_blocks_recovery_until_cleanup(self):
        self.add()
        marker = self.p / "started.txt"
        late = self.p / "late-cancel.txt"
        child = "import time,pathlib; time.sleep(3); pathlib.Path(" + repr(str(late)) + ").write_text('orphan')"
        script = "import subprocess,sys,pathlib,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); pathlib.Path(" + repr(str(marker)) + ").write_text('started'); time.sleep(30)"
        (self.p / ".uasef/runners.json").write_text(json.dumps({"profiles":{"test":{
            "type":"subprocess", "argv":[sys.executable,"-c",script], "timeout_seconds":30}}}))
        process = subprocess.Popen([sys.executable, "-m", "uasef", "dispatch", "WORK-001",
                    "--profile", "test", "--execute", "--project", str(self.p)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 20
            while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertTrue(marker.exists())
            with o.db(self.p) as conn:
                conn.execute("UPDATE tasks SET lease_until='2000-01-01' WHERE id='WORK-001'")
                self.assertEqual(o.recover_expired(conn), [])
                with self.assertRaisesRegex(ValueError, "still active"):
                    o.retry(conn, "WORK-001", "operator")
                self.assertEqual(o.cancel(conn, "WORK-001", "operator"), "cancellation requested")
            out, err = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 1, out+err)
            time.sleep(3.2)
            self.assertFalse(late.exists(), "Descendant survived cancellation")
            with o.db(self.p) as conn:
                self.assertEqual(o.task(conn, "WORK-001")["status"], "cancelled")
                self.assertEqual(conn.execute("SELECT status FROM runs").fetchone()[0], "cancelled")
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)

    def test_cancel_queued_task_never_runs(self):
        self.add()
        with o.db(self.p) as conn:
            self.assertEqual(o.cancel(conn, "WORK-001"), "cancelled")
            with self.assertRaises(ValueError):
                o.claim(conn, "WORK-001", "test")

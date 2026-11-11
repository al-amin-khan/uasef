import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import shutil
import contextlib
import io
from uasef import cli
from uasef.doctor import hooks
from uasef.doctor import diagnose
from uasef.doctor import agent_checks
from unittest.mock import patch


class DoctorTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_effective_custom_hooks_path_is_inspected_not_executed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", "custom-hooks"], check=True)
            target = root / "custom-hooks"
            target.mkdir()
            hook = target / "commit-msg"
            hook.write_text("#!/bin/sh\n# lefthook\ntouch SHOULD_NOT_EXIST\n")
            hook.chmod(0o755)
            result = []
            hooks(root, lambda *args: result.append(args))
            self.assertTrue(any("launcher detected" in row[2] for row in result))
            self.assertFalse((root / "SHOULD_NOT_EXIST").exists())

    def test_json_cli_and_error_exit(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()) as output:
            code = cli.main(["doctor", "--project", str(Path(folder) / "missing"), "--json"])
            self.assertEqual(code, 1)
            self.assertFalse(json.loads(output.getvalue())["healthy"])

    def test_default_never_invokes_agent(self):
        with patch("uasef.doctor.command") as command:
            agent_checks(lambda *args: None)
            command.assert_not_called()

    def test_live_requires_explicit_model(self):
        with self.assertRaises(ValueError):
            diagnose(".", live=True)

    def test_live_error_overrides_ack_and_hides_output(self):
        results = []
        output = json.dumps({"type": "text", "part": {"text": "UASEF_DOCTOR_OK"}}) + '\n' + json.dumps({"type": "error", "error": "SECRET"})
        with patch("uasef.doctor.shutil.which", return_value="opencode"), patch("uasef.doctor.command", return_value=(0, output)):
            agent_checks(lambda *args: results.append(args), live=True, model="provider/model")
        self.assertEqual(results[0][1], "error")
        self.assertNotIn("SECRET", str(results))

    def test_live_success_and_denied_tools(self):
        results = []
        with patch("uasef.doctor.shutil.which", return_value="opencode"), patch("uasef.doctor.command", return_value=(0, json.dumps({"type": "text", "part": {"text": "UASEF_DOCTOR_OK"}}))) as command:
            agent_checks(lambda *args: results.append(args), live=True, model="provider/model")
            self.assertEqual(command.call_args.args[3]["OPENCODE_PERMISSION"], '{"*":"deny"}')
        self.assertEqual(results[0][1], "ok")
    def test_empty_project_is_not_modified(self):
        with tempfile.TemporaryDirectory() as folder:
            result = diagnose(folder)
            self.assertTrue(result["healthy"])
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_corrupt_state_reported_without_modification(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".uasef" / "state.json"
            path.parent.mkdir()
            path.write_text("broken")
            result = diagnose(folder)
            self.assertFalse(result["healthy"])
            self.assertEqual(path.read_text(), "broken")
            json.dumps(result)

    def test_missing_project(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(diagnose(Path(folder) / "missing")["healthy"])

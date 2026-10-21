"""Offline tests of UASEF CLI, workflow guards, and portable skills."""
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest

from uasef import cli


class UasefTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / "example"

    def run_cli(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = cli.main(list(argv))
        return rc, stdout.getvalue(), stderr.getvalue()

    def create(self, adapter="all"):
        code, stdout, stderr = self.run_cli("init", str(self.p), "--name", "Demo & Co", "--idea", "Inventory and forecast app", "--adapter", adapter)
        self.assertEqual(code, 0, stderr)
        return cli.load(self.p)

    def test_init_and_portability_files(self):
        state = self.create()
        self.assertEqual(len(state["tasks"]), 16)
        self.assertEqual(sum(x["approval_required"] for x in state["tasks"]), 4)
        self.assertEqual(state["name"], "Demo & Co")
        self.assertIn("Inventory", (self.p / "docs/00-inception/idea-brief.md").read_text())
        self.assertIn("Demo & Co", (self.p / "project.yaml").read_text())
        self.assertTrue((self.p / ".claude/skills/project-inception/SKILL.md").is_file())
        self.assertTrue((self.p / ".claude/skills/project-inception/references/inception-interview.md").is_file())
        self.assertTrue((self.p / ".github/agents/software-architect.agent.md").is_file())
        self.assertTrue((self.p / ".agents/skills/technology-selection/SKILL.md").is_file())
        self.assertTrue((self.p / ".uasef/roles/researcher.md").is_file())
        self.assertEqual(self.run_cli("validate", "--project", str(self.p))[0], 0)

    def test_refuses_unsafe_existing_and_reinitialization(self):
        self.p.mkdir()
        (self.p / "keep.txt").write_text("preserve")
        self.assertEqual(self.run_cli("init", str(self.p))[0], 2)
        self.assertEqual(self.run_cli("init", str(self.p), "--existing")[0], 0)
        self.assertEqual((self.p / "keep.txt").read_text(), "preserve")
        self.assertEqual(self.run_cli("init", str(self.p), "--existing")[0], 2)

    def test_task_dependency_completion_and_handoff(self):
        self.create()
        self.assertEqual(self.run_cli("start", "INIT-002", "--project", str(self.p))[0], 2)
        self.assertEqual(self.run_cli("start", "INIT-001", "--project", str(self.p))[0], 0)
        self.assertEqual(self.run_cli("complete", "INIT-001", "--project", str(self.p))[0], 2)
        self.p.joinpath("docs/00-inception/idea-brief.md").write_text(
            "# Idea brief\n\nThe product addresses a concrete stock reconciliation problem in two small stores. "
            "Target users are store operators, and the assumptions are explicitly subject to validation.\n")
        self.assertEqual(self.run_cli("complete", "INIT-001", "--project", str(self.p))[0], 0)
        self.assertEqual(cli.load(self.p)["tasks"][0]["status"], "completed")
        self.assertEqual(self.run_cli("start", "INIT-002", "--project", str(self.p))[0], 0)
        self.assertEqual(self.run_cli("handoff", "--project", str(self.p))[0], 0)
        self.assertIn("INIT-002", (self.p / ".uasef/handoff.md").read_text())

    def test_human_gate(self):
        self.create()
        s = cli.load(self.p)
        # Make prerequisite task states represent reviewed preceding work.
        for t in s["tasks"][:4]:
            t["status"] = "completed"
            for rel in t["outputs"]:
                (self.p / rel).write_text("Verified task record with evidence references, constraints, results and remaining concerns. " * 3)
        cli.save(self.p, s)
        self.assertEqual(self.run_cli("start", "INIT-005", "--project", str(self.p))[0], 0)
        (self.p / "docs/00-inception/feasibility.md").write_text("A fully substantiated feasibility analysis with real source references and recorded risk considerations. " * 3)
        self.assertEqual(self.run_cli("complete", "INIT-005", "--project", str(self.p))[0], 0)
        self.assertEqual(cli.step(cli.load(self.p), "INIT-005")["status"], "awaiting_approval")
        self.assertEqual(self.run_cli("start", "INIT-006", "--project", str(self.p))[0], 2)
        self.assertEqual(self.run_cli("approve", "INIT-005", "--project", str(self.p), "--note", "ok")[0], 2)
        self.assertEqual(self.run_cli("approve", "INIT-005", "--project", str(self.p), "--note", "Owner accepted feasibility and risks")[0], 0)
        self.assertEqual(self.run_cli("start", "INIT-006", "--project", str(self.p))[0], 0)

    def test_feature_scaffold_no_overwrite(self):
        self.create()
        self.assertEqual(self.run_cli("feature", "stock-balance", "--project", str(self.p))[0], 0)
        self.assertTrue((self.p / "specs/features/stock-balance/verification.md").exists())
        self.assertEqual(self.run_cli("feature", "stock-balance", "--project", str(self.p))[0], 2)
        self.assertEqual(self.run_cli("feature", "../bad", "--project", str(self.p))[0], 2)

    def test_skill_spec_frontmatter(self):
        root = cli.framework_root()
        skills = list((root / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 18)
        for path in skills:
            txt = path.read_text()
            self.assertRegex(txt, r"\A---\nname: [a-z0-9-]+\ndescription: .+\n---\n")
            name = re.search(r"^name: (.+)$", txt, re.M).group(1)
            self.assertEqual(name, path.parent.name)
            self.assertLessEqual(len(name), 64)
            desc = re.search(r"^description: (.+)$", txt, re.M).group(1)
            self.assertLessEqual(len(desc), 1024)
        wf = json.loads((root / "workflows/inception.json").read_text())
        self.assertEqual([t["id"] for t in wf["tasks"]], [f"INIT-{i:03d}" for i in range(1,17)])
        for t in wf["tasks"]:
            for output in t["outputs"]:
                self.assertTrue((root / "templates" / output).is_file(), output)


if __name__ == "__main__":
    unittest.main()

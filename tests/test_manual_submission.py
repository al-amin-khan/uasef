import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from uasef import cli, orchestrator

class ManualSubmissionTests(unittest.TestCase):
    def test_submit_then_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'p'
            def run(*args):
                with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    return cli.main(list(args))
            self.assertEqual(run('init',str(p)),0)
            self.assertEqual(run('task','add','UX-001','--title','Produce wireframes', '--role','ux-designer',
                                 '--skill','ux-design','--acceptance','Document all screen states', '--project',str(p)),0)
            (p/'evidence.md').write_text('Documented the approved wireframes and reviewed alternative user experiences.')
            self.assertEqual(run('task','submit','UX-001','--actor','ux-agent','--evidence','evidence.md','--project',str(p)),0)
            with orchestrator.db(p) as conn:self.assertEqual(orchestrator.task(conn,'UX-001')['status'],'awaiting_review')
            self.assertEqual(run('task','verify','UX-001','--reviewer','qa-agent','--evidence','evidence.md','--project',str(p)),0)
            with orchestrator.db(p) as conn:self.assertEqual(orchestrator.task(conn,'UX-001')['status'],'completed')

class UpgradeTests(unittest.TestCase):
    def test_upgrade_existing_project_does_not_clobber(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'project'
            def run(*args):
                with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    return cli.main(list(args))
            self.assertEqual(run('init',str(p)),0)
            role=p/'.uasef/roles/orchestrator.md'
            role.write_text('custom role retained')
            state=cli.load(p)
            state['framework_version']='0.1.0'
            cli.save(p,state)
            (p/'.agents/skills/agent-task-orchestration/SKILL.md').unlink()
            self.assertEqual(run('upgrade','--project',str(p)),0)
            self.assertEqual(role.read_text(),'custom role retained')
            self.assertTrue((p/'.agents/skills/agent-task-orchestration/SKILL.md').exists())
            self.assertEqual(cli.load(p)['framework_version'],'0.2.0')
            self.assertEqual(run('upgrade','--project',str(p)),0)

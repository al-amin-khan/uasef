"""OpenCode CLI contract tests: no provider network or real model required."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from uasef import cli, orchestrator as orch


MOCK_CLI = '''import json, os, pathlib, sys
args=sys.argv[1:]
if args == ['--version']:
    print('opencode mock-1.0')
    sys.exit(0)
if args == ['run', '--help']:
    print('Usage: run --file --format --agent --model')
    sys.exit(0)
if not args or args[0] != 'run':
    sys.exit(4)
if '--file' not in args or '--format' not in args or '--agent' not in args:
    sys.exit(5)
file=pathlib.Path(args[args.index('--file')+1])
text=file.read_text(encoding='utf-8')
if '# UASEF Scoped Task API-001' not in text or 'backend-engineer' not in text:
    sys.exit(6)
if not str(file.resolve()).startswith(str(pathlib.Path.cwd().resolve())):
    sys.exit(7)
if 'UASEF_TASK_ID' not in os.environ:
    sys.exit(8)
if 'UASEF_LEAK_TEST_SECRET' in os.environ:
    sys.exit(9)
if os.environ.get('UASEF_ALLOWED_TEST') != 'visible':
    sys.exit(10)
print(json.dumps({'type': 'text', 'sessionID': 'ses_mock123', 'part': {'type': 'text', 'text': 'Work done'}}))
if os.environ.get('UASEF_MOCK_ERROR') == 'yes':
    print(json.dumps({'type': 'error', 'error': 'provider unavailable'}))
'''


class OpenCodeIntegration(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project=Path(tmp.name)/'app'
        self.mock=Path(tmp.name)/'mock_opencode.py'
        self.mock.write_text(MOCK_CLI, encoding='utf-8')
        self.assertEqual(self.call('init',str(self.project),'--adapter','opencode'),0,self.output)
        self.assertEqual(self.call('task','add','API-001','--title','Implement endpoint',
            '--role','backend-engineer','--skill','feature-implementation',
            '--acceptance','Tests must pass','--project',str(self.project)),0,self.output)
        self.config={
            'profiles':{'manual':{'type':'manual'},'opencode':{
                'type':'opencode','argv':[sys.executable,str(self.mock)],
                'agent':'build','timeout_seconds':20,'env_allowlist':['UASEF_ALLOWED_TEST','UASEF_MOCK_ERROR']}},
            'routing':{'defaults':['opencode'],'by_role':{}}}
        self.write_config()

    def write_config(self):
        (self.project/'.uasef/runners.json').write_text(json.dumps(self.config),encoding='utf-8')

    def call(self,*args):
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
            code=cli.main(list(args))
        self.output=buf.getvalue()
        return code

    def test_agent_export_and_skills(self):
        self.assertTrue((self.project/'.opencode/agents/backend-engineer.md').exists())
        self.assertIn('mode: subagent',(self.project/'.opencode/agents/backend-engineer.md').read_text())
        self.assertTrue((self.project/'.agents/skills/feature-implementation/SKILL.md').exists())
        self.assertFalse((self.project/'.opencode/skills').exists())
        self.assertEqual(self.call('validate','--project',str(self.project)),0,self.output)

    def test_preview_does_not_execute(self):
        self.assertEqual(self.call('dispatch','API-001','--profile','opencode','--project',str(self.project)),0,self.output)
        self.assertIn('Dry run only',self.output)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'queued')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM runs').fetchone()[0],0)

    def test_doctor(self):
        self.assertEqual(self.call('opencode','doctor','--project',str(self.project)),0,self.output)
        self.assertIn('flags verified',self.output)

    def test_execute_and_summary(self):
        with patch.dict(os.environ,{'UASEF_ALLOWED_TEST':'visible','UASEF_LEAK_TEST_SECRET':'private'}):
            self.assertEqual(self.call('dispatch','API-001','--profile','auto','--execute','--project',str(self.project)),0,self.output)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'awaiting_review')
            log=Path(db.execute('SELECT log_path FROM runs').fetchone()[0])
        summary=json.loads(log.with_name('opencode-summary.json').read_text())
        self.assertEqual(summary['events'],1)
        self.assertEqual(summary['session_ids'],['ses_mock123'])
        self.assertEqual(summary['errors'],[])
        self.assertFalse(summary['verified'])
        self.assertIn('"type": "text"',log.read_text())
        self.assertTrue(log.with_name('runner.stderr.log').exists())

    def test_error_event_fails_run_even_exit_zero(self):
        with patch.dict(os.environ,{'UASEF_ALLOWED_TEST':'visible','UASEF_MOCK_ERROR':'yes'}):
            self.assertEqual(self.call('dispatch','API-001','--profile','opencode','--execute','--project',str(self.project)),0,self.output)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'failed')
            self.assertEqual(db.execute('SELECT exit_code FROM runs').fetchone()[0],1)

    def test_invalid_profile_does_not_claim_task(self):
        self.config['profiles']['opencode']['model']='not a valid model'
        self.write_config()
        self.assertEqual(self.call('dispatch','API-001','--profile','opencode','--execute','--project',str(self.project)),2)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'queued')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM runs').fetchone()[0],0)

    def test_missing_executable_does_not_claim_task(self):
        self.config['profiles']['opencode']['argv']=['opencode-unknown-binary-uasef-test']
        self.write_config()
        self.assertEqual(self.call('dispatch','API-001','--profile','opencode','--execute','--project',str(self.project)),2)
        self.assertIn('not found',self.output)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'queued')

    def test_git_worktree_prompt_is_inside_workspace(self):
        subprocess.run(['git','init','-q',str(self.project)],check=True)
        subprocess.run(['git','-C',str(self.project),'add','AGENTS.md','.agents','.opencode'],check=True)
        subprocess.run(['git','-C',str(self.project),'-c','user.name=Test','-c','user.email=test@example.com','commit','-qm','baseline'],check=True)
        with patch.dict(os.environ,{'UASEF_ALLOWED_TEST':'visible'}):
            self.assertEqual(self.call('dispatch','API-001','--profile','opencode','--execute','--worktree','--project',str(self.project)),0,self.output)
        with orch.db(self.project) as db:
            self.assertEqual(orch.task(db,'API-001')['status'],'awaiting_review')
            run=db.execute('SELECT workspace FROM runs').fetchone()[0]
        self.assertTrue((Path(run)/'.opencode/agents/backend-engineer.md').exists())
        self.assertTrue(list((Path(run)/'.uasef/runs').glob('*/opencode-task.md')))


if __name__ == '__main__':
    unittest.main()

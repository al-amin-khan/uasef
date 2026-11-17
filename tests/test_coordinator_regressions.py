"""Regression coverage for audit F01 and F03 using real runner processes."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from uasef import cli, executor, orchestrator as o


class CoordinatorRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / 'project'
        self.assertEqual(self.call('init', str(self.p)), 0)

    def call(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = cli.main(list(args))
        self.output = output.getvalue()
        return code

    def add(self, identifier, depends=(), parent=None):
        with o.db(self.p) as conn:
            return o.add_task(conn, self.p, identifier, identifier, 'backend-engineer',
                              'feature-implementation', 'Check observable behavior',
                              depends=depends, parent_id=parent)

    def profile(self, argv, timeout=10):
        (self.p / '.uasef/runners.json').write_text(json.dumps({'profiles':{
            'test': {'type':'subprocess', 'argv':argv, 'timeout_seconds':timeout}}}))

    def test_real_cli_failure_reaches_operating_system(self):
        self.add('FAIL-001')
        self.profile([sys.executable, '-c', 'raise SystemExit(7)'])
        result = subprocess.run([sys.executable, '-m', 'uasef', 'dispatch', 'FAIL-001',
                                 '--profile', 'test', '--execute', '--project', str(self.p)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn, 'FAIL-001')['status'], 'failed')
            self.assertEqual(conn.execute('SELECT exit_code FROM runs').fetchone()[0], 7)

    def test_timeout_and_missing_program_are_failures(self):
        for identifier, argv, expected in (
            ('TIME-001', [sys.executable, '-c', 'import time; time.sleep(5)'], 124),
            ('MISS-001', [str(self.p / 'missing-program')], 127),
        ):
            self.add(identifier)
            self.profile(argv, timeout=1)
            self.assertEqual(self.call('dispatch', identifier, '--profile', 'test',
                                       '--execute', '--project', str(self.p)), 1, self.output)
            with o.db(self.p) as conn:
                row = conn.execute('SELECT exit_code FROM runs WHERE task_id=?', (identifier,)).fetchone()
                self.assertEqual(row[0], expected)

    def test_large_prompt_timeout_and_stdin_delivery(self):
        prompt = self.p / 'large-prompt.txt'
        prompt.write_bytes(b'x' * 1024 * 1024)
        log = self.p / 'runner.log'
        profile = {'type': 'subprocess', 'timeout_seconds': 1,
                   'argv': [sys.executable, '-c', 'import time; time.sleep(5)']}
        code, error = executor.execute(self.p, 'test', profile, prompt, log, self.p, 'TIME-001')
        self.assertEqual(code, 124, error)
        profile['timeout_seconds'] = 10
        profile['argv'] = [sys.executable, '-c',
                           'import sys; print(len(sys.stdin.buffer.read()))']
        code, error = executor.execute(self.p, 'test', profile, prompt, log, self.p, 'READ-001')
        self.assertEqual(code, 0, error)
        self.assertEqual(log.read_text().strip(), str(1024 * 1024))

    def mixed_batch(self, parallel):
        self.add('FAIL-001'); self.add('PASS-001')
        self.profile([sys.executable, '-c', "import os,sys; sys.stdin.read(); sys.exit(7 if os.environ['UASEF_TASK_ID']=='FAIL-001' else 0)"])
        flags = []
        if parallel:
            for args in [('init',), ('config', 'user.name', 'Test'),
                         ('config', 'user.email', 'test@example.invalid'), ('add', '.'),
                         ('commit', '-m', 'test: initial project')]:
                subprocess.run(['git', '-C', str(self.p), *args], capture_output=True, check=True)
            flags = ['--jobs', '2', '--worktree']
        self.assertEqual(self.call('dispatch-ready', '--profile', 'test', '--execute',
                                   '--project', str(self.p), *flags), 1, self.output)
        self.assertIn('FAIL-001', self.output); self.assertIn('PASS-001', self.output)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn, 'FAIL-001')['status'], 'failed')
            self.assertEqual(o.task(conn, 'PASS-001')['status'], 'awaiting_review')

    def test_sequential_batch_preserves_mixed_results(self):
        self.mixed_batch(False)

    def test_parallel_batch_preserves_mixed_results(self):
        self.mixed_batch(True)

    def test_blocked_batch_reports_all_tasks(self):
        self.add('TASK-001'); self.add('TASK-002')
        self.assertEqual(self.call('dispatch-ready', '--profile', 'missing', '--execute',
                                   '--project', str(self.p)), 2)
        self.assertIn('TASK-001', self.output); self.assertIn('TASK-002', self.output)
        with o.db(self.p) as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM runs').fetchone()[0], 0)

    def test_parent_child_cycle_rejected_without_partial_write(self):
        self.add('PARENT-001')
        with self.assertRaisesRegex(ValueError, 'dependency/delegation cycle'):
            self.add('CHILD-001', depends=['PARENT-001'], parent='PARENT-001')
        with o.db(self.p) as conn:
            self.assertEqual(len(o.list_tasks(conn)), 1)
            self.assertEqual(conn.execute("SELECT count(*) FROM audit WHERE event='delegated'").fetchone()[0], 0)
        self.add('CHILD-001', parent='PARENT-001')

    def test_transitive_dependency_and_ancestor_cycles(self):
        self.add('ROOT-001')
        self.add('MIDDLE-001', depends=['ROOT-001'])
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.add('CHILD-001', depends=['MIDDLE-001'], parent='ROOT-001')
        self.add('CHILD-001', parent='ROOT-001')
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.add('LEAF-001', depends=['ROOT-001'], parent='CHILD-001')

    def test_sibling_ordering_remains_valid(self):
        self.add('ROOT-001')
        self.add('CHILD-001', parent='ROOT-001')
        self.add('CHILD-002', parent='ROOT-001', depends=['CHILD-001'])
        with o.db(self.p) as conn:
            self.assertTrue(o.eligible(conn, o.task(conn, 'CHILD-001')))
            self.assertFalse(o.eligible(conn, o.task(conn, 'CHILD-002')))

import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uasef import cli, memory as m, orchestrator as o, sessions, executor


class ReviewRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / 'project'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(['init', str(self.p)]), 0)

    def task(self, identifier='API-001'):
        with o.db(self.p) as conn:
            return o.add_task(conn, self.p, identifier, 'Task', 'backend-engineer',
                              'feature-implementation', 'Test behavior')

    def test_corruption_reports_filename_and_does_not_fail_saved_task(self):
        record = m.records(self.p)[0]
        path = m.directory(self.p) / 'records' / (record['id'] + '.json')
        original = path.read_text()
        record.pop('at')
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, path.name):
            m.records(self.p)
        warning = io.StringIO()
        with contextlib.redirect_stderr(warning):
            self.task()
        self.assertIn('task state is saved', warning.getvalue())
        with contextlib.closing(sqlite3.connect(self.p / '.uasef/orchestration.sqlite3')) as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM tasks').fetchone()[0], 1)
        path.write_text(original)
        m.sync(self.p)
        self.assertTrue(any(r['task'] == 'API-001' for r in m.records(self.p)))

    def test_default_prompt_includes_checkpoint_but_excludes_other_task(self):
        task = self.task()
        self.task('API-002')
        with o.db(self.p) as conn:
            for identifier, message in [('API-001', 'NEXT_STEP_UNIQUE'), ('API-002', 'UNRELATED_UNIQUE')]:
                session = sessions.start(conn, identifier, 'Session')
                sessions.record(conn, self.p, session['id'], 'checkpoint', 'model', message)
        prompt = executor.build_prompt(self.p, task)
        self.assertIn('NEXT_STEP_UNIQUE', prompt)
        self.assertNotIn('UNRELATED_UNIQUE', prompt)

    def test_unexpected_file_rejected_before_index_changes(self):
        m.git(self.p, 'init', required=True)
        extra = m.directory(self.p) / 'credentials.txt'
        extra.write_text('SYNTHETIC_ONLY')
        with self.assertRaisesRegex(ValueError, 'Unexpected file'):
            m.checkpoint(self.p, 'docs: checkpoint')
        self.assertEqual(m.git(self.p, 'diff', '--cached', '--name-only', required=True), '')

    def test_malformed_nested_fields_are_rejected(self):
        original = m.records(self.p)[0]
        for key, value in [('links', [1]), ('data', []), ('evidence', [{}]), ('git', None), ('at', 'invalid')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.validate_record(dict(original, **{key: value}), original['id'])

    def test_checkpoint_respects_commit_msg_hook_failure(self):
        m.git(self.p, 'init', required=True)
        m.git(self.p, 'config', 'user.name', 'Review', required=True)
        m.git(self.p, 'config', 'user.email', 'review@example.invalid', required=True)
        hook = self.p / '.git/hooks/commit-msg'
        hook.write_bytes(b'#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'Git failed'):
            m.checkpoint(self.p, 'docs: checkpoint')
        self.assertIsNone(m.git(self.p, 'rev-parse', '--verify', 'HEAD'))

"""Guided intake behavior, cancellation, and compatibility."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uasef import cli


class IntakeTests(unittest.TestCase):
    def run_setup(self, target, responses, *flags):
        with patch('builtins.input', side_effect=responses), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(['init', str(target), '-i', *flags])

    def test_create_persists_answers_without_approving_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'demo'
            answers = ['', 'Demo', 'Track stock', 'Store owners', 'Stock entry', 'Billing', 'Help me choose', 'No budget', 'Accurate counts', 'codex', 'create']
            self.assertEqual(self.run_setup(target, answers), 0)
            state = cli.load(target)
            self.assertIn('Store owners', state['idea'])
            self.assertIn('No budget', (target / 'docs/00-inception/idea-brief.md').read_text(encoding='utf-8'))
            self.assertTrue(all(t['status'] == 'pending' for t in state['tasks']))

    def test_cancel_interrupt_and_eof_create_nothing(self):
        for ending in ('cancel', EOFError(), KeyboardInterrupt()):
            with self.subTest(ending=ending), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / 'demo'
                self.assertEqual(self.run_setup(target, ['', '', 'Idea'] + [''] * 7 + [ending]), 0)
                self.assertFalse(target.exists())

    def test_edit_and_invalid_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'demo'
            first = ['', '', 'Old idea'] + [''] * 6 + ['invalid', 'codex', 'edit']
            second = ['', '', 'New idea'] + [''] * 7 + ['create']
            self.assertEqual(self.run_setup(target, first + second), 0)
            self.assertTrue(cli.load(target)['idea'].startswith('New idea'))

    def test_existing_files_remain_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            keep = target / 'README.md'
            keep.write_text('Keep this', encoding='utf-8')
            self.assertEqual(self.run_setup(target, ['']), 2)
            self.assertFalse((target / '.uasef').exists())
            self.assertEqual(self.run_setup(target, ['', '', 'Idea'] + [''] * 7 + ['create'], '--existing'), 0)
            self.assertEqual(keep.read_text(encoding='utf-8'), 'Keep this')

"""Cross-feature upgrade compatibility for the consolidated delivery baseline."""
import contextlib
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uasef import cli, memory, orchestrator


class ConsolidationTests(unittest.TestCase):
    def test_legacy_export_before_design_schema_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'project'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['init', str(p)]), 0)
            with orchestrator.db(p) as conn:
                orchestrator.add_task(conn, p, 'API-001', 'API', 'backend-engineer',
                                      'feature-implementation', 'Existing task survives')
            with contextlib.closing(sqlite3.connect(orchestrator.database_path(p))) as conn:
                for column in ('design_gate_required', 'design_task_id', 'design_waiver'):
                    conn.execute('ALTER TABLE tasks DROP COLUMN ' + column)
                conn.commit()
            memory.sync(p)
            self.assertTrue(any(r['task'] == 'API-001' for r in memory.records(p)))
            with orchestrator.db(p) as conn:
                self.assertFalse(orchestrator.task(conn, 'API-001')['design_gate_required'])
                self.assertEqual(orchestrator.task(conn, 'API-001')['status'], 'queued')

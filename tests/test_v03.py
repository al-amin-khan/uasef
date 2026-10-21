"""Regression tests for opt-in v0.3 sessions, routing and delegation."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from uasef import cli, orchestrator as o, sessions, routing


class V03(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.p=Path(tmp.name)/"app"
        self.assertEqual(self.call("init",str(self.p),"--name","Demo"),0,self.out)
        self.p.joinpath("docs/evidence").mkdir(parents=True)
        (self.p/"docs/evidence/check.txt").write_text("review evidence")

    def call(self,*argv):
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
            result=cli.main(list(argv))
        self.out=buf.getvalue()
        return result

    def add(self,id,parent=None):
        v=["task","add",id,"--title",id,"--role","backend-engineer","--skill","feature-implementation","--acceptance","Implementation is independently tested","--project",str(self.p)]
        if parent:v.extend(["--parent",parent])
        self.assertEqual(self.call(*v),0,self.out)

    def test_sessions_checkpoint_export_and_close(self):
        self.add("API-001")
        with o.db(self.p) as c:
            s=sessions.start(c,"API-001","First run")
            sid=s['id']
            sessions.record(c,self.p,sid,"checkpoint","model-A","Inspected API contract",["docs/evidence/check.txt"])
            handoff=sessions.export(c,self.p,sid)
            self.assertIn("Inspected API contract",handoff.read_text())
            self.assertEqual(len(sessions.events(c,sid)),2)
            sessions.close(c,sid,"operator","Switching to another model")
            with self.assertRaises(ValueError):sessions.record(c,self.p,sid,"note","model-B","Should fail")

    def test_sessions_reject_path_traversal_and_foreign_task(self):
        self.add("API-001");self.add("API-002")
        with o.db(self.p) as c:
            s=sessions.start(c,"API-001","First run")
            with self.assertRaises(ValueError):sessions.record(c,self.p,s['id'],"checkpoint","A","Saved",["../../etc/passwd"])
        self.assertEqual(self.call("dispatch","API-002","--session",s['id'],"--project",str(self.p)),2)

    def test_parent_cannot_pass_review_while_child_incomplete(self):
        self.add("API-001");self.add("API-002",parent="API-001")
        with o.db(self.p) as c:
            self.assertEqual(o.task(c,"API-002")["parent_id"],"API-001")
            o.submit_manual(c,self.p,"API-001","coder",["docs/evidence/check.txt"])
            with self.assertRaises(ValueError):o.verify(c,self.p,"API-001","reviewer",["docs/evidence/check.txt"])
            o.submit_manual(c,self.p,"API-002","coder",["docs/evidence/check.txt"])
            o.verify(c,self.p,"API-002","reviewer",["docs/evidence/check.txt"])
            o.verify(c,self.p,"API-001","reviewer",["docs/evidence/check.txt"])
            self.assertEqual(o.task(c,"API-001")["status"],"completed")

    def test_parent_cannot_delegate_from_closed(self):
        self.add("API-001")
        with o.db(self.p) as c:
            o.submit_manual(c,self.p,"API-001","coder",["docs/evidence/check.txt"])
            o.verify(c,self.p,"API-001","reviewer",["docs/evidence/check.txt"])
        self.assertEqual(self.call("task","delegate","API-002","--parent","API-001","--title","Child","--role","qa-engineer","--skill","quality-verification","--acceptance","Tests done","--project",str(self.p)),2)

    def test_routing_auto_and_role_enforcement(self):
        self.add("API-001")
        c={"profiles":{"manual":{"type":"manual"},"disabled":{"type":"subprocess","enabled":False},"reviewer":{"type":"subprocess","argv":[sys.executable,"-c","print('ok')"],"roles":["qa-engineer"]},"coder":{"type":"subprocess","argv":[sys.executable,"-c","import sys;sys.stdin.read();print('ok')"],"roles":["backend-engineer"],"timeout_seconds":5}},"routing":{"by_role":{"backend-engineer":["disabled","reviewer","coder"]},"defaults":[]}}
        (self.p/".uasef/runners.json").write_text(json.dumps(c))
        with o.db(self.p) as db:
            t=o.task(db,"API-001")
        self.assertEqual(routing.select(c,t),"coder")
        self.assertEqual(self.call("dispatch","API-001","--profile","auto","--project",str(self.p)),0,self.out)
        self.assertIn("Selected coder",self.out)
        self.assertEqual(self.call("dispatch","API-001","--profile","reviewer","--execute","--project",str(self.p)),2,self.out)
        self.assertEqual(self.call("dispatch","API-001","--profile","auto","--execute","--project",str(self.p)),0,self.out)
        with o.db(self.p) as db:
            self.assertEqual(o.task(db,"API-001")["status"],"awaiting_review")

    def test_new_cli_commands(self):
        self.add("API-001")
        self.assertEqual(self.call("session","start","--task","API-001","--name","Investigation","--project",str(self.p)),0,self.out)
        self.assertEqual(self.call("task","delegate","API-TEST","--parent","API-001","--title","Review","--role","qa-engineer","--skill","quality-verification","--acceptance","Tests pass","--project",str(self.p)),0,self.out)
        self.assertEqual(self.call("task","tree","--project",str(self.p)),0)
        self.assertIn("API-TEST",self.out)

    def test_additive_migration(self):
        self.add("API-001")
        with o.db(self.p) as db:
            self.assertIn("parent_id",[r[1] for r in db.execute("PRAGMA table_info(tasks)")])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],0)

if __name__ == "__main__":unittest.main()

"""Real orchestration behavior: subprocess, transactions, approvals, recovery."""
import contextlib
from datetime import timedelta
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
from uasef import cli, orchestrator as o


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p=Path(self.temp.name)/"sample"
        self.assertEqual(self.invoke("init",str(self.p),"--name","Demo"),0)
        self.p.joinpath("docs/evidence").mkdir(parents=True)
        self.p.joinpath("docs/evidence/review.md").write_text("Independent review inspected the logs, changes, outputs and relevant acceptance checks.")

    def invoke(self,*args):
        out=io.StringIO();err=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=cli.main(list(args))
        self.message=out.getvalue()+err.getvalue()
        return code

    def add(self,id="TASK-001",depends=(),approval=False):
        command=["task","add",id,"--title",f"Implement {id}","--role","backend-engineer",
                 "--skill","feature-implementation","--acceptance","Satisfy API contract and run automated tests",
                 "--project",str(self.p)]
        for d in depends: command.extend(["--depends",d])
        if approval:command.append("--approval-required")
        self.assertEqual(self.invoke(*command),0,self.message)

    def profile(self,exit_code=0):
        settings={"profiles":{"manual":{"type":"manual"},"mock":{"type":"subprocess", "argv":[sys.executable,"-c",f"import sys; prompt=sys.stdin.read(); print('received=',len(prompt)); sys.exit({exit_code})"],"timeout_seconds":15}}}
        (self.p/".uasef/runners.json").write_text(json.dumps(settings))

    def test_manual_preview_and_opt_in(self):
        self.add()
        self.assertEqual(self.invoke("dispatch","TASK-001","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:self.assertEqual(o.task(conn,"TASK-001")["status"],"queued")
        self.profile()
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--project",str(self.p)),0)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["status"],"queued")
            self.assertEqual(conn.execute("SELECT count(*) FROM runs").fetchone()[0],0)
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--execute","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["status"],"awaiting_review")
            log=conn.execute("SELECT log_path FROM runs").fetchone()[0]
        self.assertIn("received=",Path(log).read_text())
        self.assertEqual(self.invoke("task","verify","TASK-001","--reviewer","mock","--evidence","docs/evidence/review.md","--project",str(self.p)),2)
        self.assertEqual(self.invoke("task","verify","TASK-001","--reviewer","qa-reviewer","--evidence","docs/evidence/review.md","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:self.assertEqual(o.task(conn,"TASK-001")["status"],"completed")

    def test_dependencies_and_approval_gate(self):
        self.add(approval=True)
        self.add("TASK-002",depends=["TASK-001"])
        self.profile()
        self.assertEqual(self.invoke("dispatch","TASK-002","--profile","mock","--execute","--project",str(self.p)),2)
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--execute","--project",str(self.p)),0,self.message)
        self.assertEqual(self.invoke("task","verify","TASK-001","--reviewer","security-reviewer","--evidence","docs/evidence/review.md","--project",str(self.p)),0)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["status"],"awaiting_approval")
            self.assertEqual(o.eligible(conn,o.task(conn,"TASK-002")),False)
        self.assertEqual(self.invoke("task","approve","TASK-001","--actor","Owner","--note","Approved risk and implementation","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:self.assertTrue(o.eligible(conn,o.task(conn,"TASK-002")))

    def test_runner_error_retry_and_audit(self):
        self.add()
        self.profile(exit_code=7)
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--execute","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["status"],"failed")
            self.assertEqual(o.task(conn,"TASK-001")["attempts"],1)
        self.assertEqual(self.invoke("task","retry","TASK-001","--project",str(self.p)),0)
        self.profile(exit_code=0)
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--execute","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["attempts"],2)
            self.assertEqual(conn.execute("SELECT count(*) FROM runs").fetchone()[0],2)
            self.assertGreater(conn.execute("SELECT count(*) FROM audit").fetchone()[0],3)

    def test_atomic_claim_across_connections(self):
        self.add()
        results=[]
        barrier=threading.Barrier(2)
        def take():
            with o.db(self.p) as conn:
                barrier.wait(timeout=5)
                try:
                    results.append(("ok",o.claim(conn,"TASK-001","runner")))
                except ValueError:
                    results.append(("blocked",None))
        threads=[threading.Thread(target=take) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=8)
        self.assertEqual(sorted(x[0] for x in results),["blocked","ok"])
        with o.db(self.p) as conn:self.assertEqual(o.task(conn,"TASK-001")["attempts"],1)

    def test_expired_lease_recovery(self):
        self.add()
        with o.db(self.p) as conn:
            o.claim(conn,"TASK-001","runner",lease_seconds=1)
            conn.execute("UPDATE tasks SET lease_until='2000-01-01T00:00:00+00:00' WHERE id='TASK-001'")
        self.assertEqual(self.invoke("task","recover","--project",str(self.p)),0)
        with o.db(self.p) as conn:
            self.assertEqual(o.task(conn,"TASK-001")["status"],"failed")
            self.assertEqual(conn.execute("SELECT status FROM runs").fetchone()[0],"interrupted")

    def test_rejects_bad_context_paths_and_duplicate(self):
        self.add()
        self.assertEqual(self.invoke("task","add","TASK-001","--title","again","--role","backend-engineer","--skill","feature-implementation","--acceptance","x","--project",str(self.p)),2)
        self.assertEqual(self.invoke("task","add","TASK-003","--title","bad path","--role","backend-engineer","--skill","feature-implementation","--acceptance","x","--context","../../etc/passwd","--project",str(self.p)),2)
        self.assertEqual(self.invoke("dispatch-ready","--jobs","2","--execute","--project",str(self.p)),2)

    def test_parallel_worktrees(self):
        import subprocess
        self.add('API-001');self.add('API-002')
        self.profile()
        subprocess.run(['git','init','-q',str(self.p)],check=True)
        subprocess.run(['git','-C',str(self.p),'-c','user.name=Test','-c','user.email=test@example.org','add','AGENTS.md'],check=True)
        subprocess.run(['git','-C',str(self.p),'-c','user.name=Test','-c','user.email=test@example.org','commit','-qm','base'],check=True)
        self.assertEqual(self.invoke('dispatch-ready','--profile','mock','--execute','--jobs','2','--worktree','--project',str(self.p)),0,self.message)
        with o.db(self.p) as conn:
            self.assertEqual([o.task(conn,id)['status'] for id in ('API-001','API-002')],['awaiting_review','awaiting_review'])
            self.assertEqual(conn.execute("SELECT COUNT(DISTINCT workspace) FROM runs").fetchone()[0],2)

    def test_worktree(self):
        import subprocess
        self.add()
        self.profile()
        subprocess.run(["git","init","-q",str(self.p)],check=True)
        subprocess.run(["git","-C",str(self.p),"-c","user.name=Test","-c","user.email=test@example.org","add","AGENTS.md"],check=True)
        subprocess.run(["git","-C",str(self.p),"-c","user.name=Test","-c","user.email=test@example.org","commit","-qm","initial"],check=True)
        self.assertEqual(self.invoke("dispatch","TASK-001","--profile","mock","--execute","--worktree","--project",str(self.p)),0,self.message)
        with o.db(self.p) as conn:
            workdir=Path(conn.execute("SELECT workspace FROM runs").fetchone()[0])
        self.assertTrue((workdir/"AGENTS.md").is_file())
        self.assertNotEqual(workdir,self.p)




if __name__ == "__main__":unittest.main()

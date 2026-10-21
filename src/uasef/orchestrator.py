"""Transactional local orchestration for UASEF tasks.

SQLite is authoritative for execution state. This is a single-machine orchestrator,
not a distributed job queue or a security boundary. Every state change is audited.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sqlite3
import uuid

TASK_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$")
TERMINAL = {"completed", "cancelled"}


def utcnow():
    return datetime.now(timezone.utc)


def timestamp():
    return utcnow().isoformat(timespec="seconds")


def database_path(project):
    return Path(project).resolve() / ".uasef" / "orchestration.sqlite3"


@contextmanager
def db(project):
    target = database_path(project)
    if not (target.parent / "state.json").is_file():
        raise ValueError("Not a UASEF project; initialize it first")
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, timeout=15, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=15000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY, title TEXT NOT NULL, role TEXT NOT NULL,
      skill TEXT NOT NULL, acceptance TEXT NOT NULL,
      context_paths TEXT NOT NULL, dependencies TEXT NOT NULL,
      needs_approval INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL DEFAULT 'queued',
      lease_token TEXT, lease_until TEXT, attempts INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
      CHECK (status IN ('queued','running','awaiting_review','awaiting_approval',
                        'completed','failed','cancelled'))
    );
    CREATE TABLE IF NOT EXISTS runs (
      id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
      profile TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
      exit_code INTEGER, status TEXT NOT NULL, prompt_path TEXT,
      log_path TEXT, workspace TEXT, error TEXT
    );
    CREATE TABLE IF NOT EXISTS audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      at TEXT NOT NULL, task_id TEXT NOT NULL REFERENCES tasks(id),
      event TEXT NOT NULL, actor TEXT NOT NULL, detail TEXT NOT NULL
    );
    """)
    try:
        yield conn
    finally:
        conn.close()


def audit(conn, task, event, actor="system", detail=""):
    conn.execute("INSERT INTO audit(at,task_id,event,actor,detail) VALUES(?,?,?,?,?)",
                 (timestamp(), task, event, actor, detail[:4000]))


def as_dict(row):
    if row is None:
        raise ValueError("Unknown task")
    task = dict(row)
    for field in ("context_paths", "dependencies"):
        task[field] = json.loads(task[field])
    task["needs_approval"] = bool(task["needs_approval"])
    return task


def task(conn, task_id):
    return as_dict(conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())


def list_tasks(conn):
    return [as_dict(x) for x in conn.execute("SELECT * FROM tasks ORDER BY created_at,id")]


def add_task(conn, project, task_id, title, role, skill, acceptance, depends=(), context=(), approval=False):
    if not TASK_ID.fullmatch(task_id) or len(task_id) > 80:
        raise ValueError("Task ID must be uppercase alphanumeric with hyphens (e.g. API-001)")
    if not title.strip() or not acceptance.strip():
        raise ValueError("Title and explicit acceptance criteria are required")
    base = Path(project).resolve()
    if not (base / ".uasef" / "roles" / f"{role}.md").is_file():
        raise ValueError(f"Unknown role {role}")
    if not (base / ".agents" / "skills" / skill / "SKILL.md").is_file():
        raise ValueError(f"Unknown skill {skill}")
    depends, context = list(dict.fromkeys(depends)), list(dict.fromkeys(context))
    if task_id in depends:
        raise ValueError("Task may not depend on itself")
    for d in depends:
        task(conn, d)  # existing-task-only dependencies prevent cycles
    from .executor import safe_document
    for filename in context:
        safe_document(base, filename)
    t = timestamp()
    try:
        with conn:
            conn.execute("INSERT INTO tasks(id,title,role,skill,acceptance,context_paths,dependencies,needs_approval,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (task_id,title,role,skill,acceptance,json.dumps(context),json.dumps(depends),int(approval),t,t))
            audit(conn, task_id, "created", detail=f"depends={depends}; approval={approval}")
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Task already exists or violates constraints: {task_id}") from e
    return task(conn, task_id)


def eligible(conn, row):
    if row["status"] != "queued":
        return False
    return all(task(conn, d)["status"] == "completed" for d in row["dependencies"])


def ready_tasks(conn):
    return [x for x in list_tasks(conn) if eligible(conn, x)]


def claim(conn, task_id, profile, lease_seconds=3600):
    token = uuid.uuid4().hex
    expiry = (utcnow() + timedelta(seconds=lease_seconds)).isoformat(timespec="seconds")
    # BEGIN IMMEDIATE serializes claims across independently running workers.
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn, task_id)
        if not eligible(conn, t):
            raise ValueError("Task is not ready (status or dependencies block execution)")
        now = timestamp()
        conn.execute("UPDATE tasks SET status='running', lease_token=?, lease_until=?, attempts=attempts+1, updated_at=? WHERE id=?",
                     (token, expiry, now, task_id))
        run_id = uuid.uuid4().hex
        conn.execute("INSERT INTO runs(id,task_id,profile,started_at,status) VALUES (?,?,?,?,?)",
                     (run_id,task_id,profile,now,"running"))
        audit(conn, task_id, "claimed", actor=profile, detail=f"run={run_id}")
        conn.commit()
        return run_id, token
    except Exception:
        conn.rollback()
        raise


def finish_run(conn, task_id, run_id, token, exit_code, prompt_path, log_path, workspace, error=""):
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn, task_id)
        if t["status"] != "running" or t["lease_token"] != token:
            raise ValueError("Lease mismatch; task may have been recovered by another worker")
        outcome = "awaiting_review" if exit_code == 0 else "failed"
        conn.execute("UPDATE tasks SET status=?, lease_token=NULL, lease_until=NULL, updated_at=? WHERE id=?",
                     (outcome,timestamp(),task_id))
        cur = conn.execute("UPDATE runs SET finished_at=?, exit_code=?, status=?, prompt_path=?, log_path=?, workspace=?, error=? WHERE id=? AND task_id=? AND status='running'",
                           (timestamp(),exit_code,outcome,str(prompt_path),str(log_path),str(workspace),error[:1000],run_id,task_id))
        if cur.rowcount != 1:
            raise ValueError("Run not found or already finalized")
        audit(conn, task_id, "run_finished", detail=f"run={run_id}; exit={exit_code}; status={outcome}")
        conn.commit()
        return outcome
    except Exception:
        conn.rollback()
        raise


def verify(conn, project, task_id, reviewer, evidence):
    if not reviewer.strip() or reviewer.strip().lower() == "agent":
        raise ValueError("Specify the named reviewer; this is a local assertion, not authenticated")
    if not evidence:
        raise ValueError("At least one existing review/test evidence file is required")
    from .executor import safe_document
    base = Path(project).resolve()
    for rel in evidence:
        safe_document(base, rel)
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn,task_id)
        if t["status"] != "awaiting_review":
            raise ValueError("Task must be awaiting_review")
        last = conn.execute("SELECT profile FROM runs WHERE task_id=? ORDER BY started_at DESC,id DESC LIMIT 1",(task_id,)).fetchone()
        manual = conn.execute("SELECT actor FROM audit WHERE task_id=? AND event='manual_submitted' ORDER BY id DESC LIMIT 1",(task_id,)).fetchone()
        if (last and reviewer.casefold() == last["profile"].casefold()) or (manual and reviewer.casefold() == manual["actor"].casefold()):
            raise ValueError("The execution profile or submitting actor cannot claim independent review")
        status = "awaiting_approval" if t["needs_approval"] else "completed"
        conn.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?",(status,timestamp(),task_id))
        audit(conn,task_id,"verified",actor=reviewer,detail=json.dumps(evidence))
        conn.commit()
        return status
    except Exception:
        conn.rollback()
        raise


def submit_manual(conn, project, task_id, actor, evidence):
    """Record an externally performed/manual agent task for independent review.

    This never asserts tests passed; a separate review step is mandatory.
    """
    if not actor.strip() or not evidence:
        raise ValueError("Manual submission requires actor and evidence files")
    from .executor import safe_document
    for rel in evidence:
        safe_document(Path(project).resolve(), rel)
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn,task_id)
        if not eligible(conn,t):
            raise ValueError("Manual submission only allowed for a ready queued task")
        conn.execute("UPDATE tasks SET status='awaiting_review',updated_at=? WHERE id=?",(timestamp(),task_id))
        audit(conn,task_id,"manual_submitted",actor=actor,detail=json.dumps(evidence))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def approve(conn, task_id, actor, note):
    if len(actor.strip()) < 2 or len(note.strip()) < 12:
        raise ValueError("Name an approver and provide a substantive approval note")
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn,task_id)
        if t["status"] != "awaiting_approval":
            raise ValueError("Only reviewed approval-gated tasks can be approved")
        conn.execute("UPDATE tasks SET status='completed',updated_at=? WHERE id=?",(timestamp(),task_id))
        audit(conn,task_id,"approved",actor=actor,detail=note)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def retry(conn, task_id, actor):
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn,task_id)
        if t["status"] != "failed":
            raise ValueError("Only failed tasks can be retried; running tasks require lease recovery")
        conn.execute("UPDATE tasks SET status='queued',updated_at=? WHERE id=?",(timestamp(),task_id))
        audit(conn,task_id,"retry",actor=actor)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def recover_expired(conn, actor="operator"):
    recovered = []
    conn.execute("BEGIN IMMEDIATE")
    try:
        for row in conn.execute("SELECT id,lease_token FROM tasks WHERE status='running' AND lease_until<?",(timestamp(),)):
            task_id = row["id"]
            conn.execute("UPDATE tasks SET status='failed',lease_token=NULL,lease_until=NULL,updated_at=? WHERE id=?",(timestamp(),task_id))
            conn.execute("UPDATE runs SET status='interrupted',finished_at=?,error='Lease expired; verify external process stopped before retry' WHERE task_id=? AND status='running'",(timestamp(),task_id))
            audit(conn,task_id,"lease_expired",actor=actor,detail="Marked failed; inspect worker before retry")
            recovered.append(task_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return recovered

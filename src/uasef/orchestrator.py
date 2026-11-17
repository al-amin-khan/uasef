"""Transactional local orchestration for UASEF tasks.

SQLite is authoritative for execution state. This is a single-machine orchestrator,
not a distributed job queue or a security boundary. Every state change is audited.
"""
from __future__ import annotations

from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
from graphlib import CycleError, TopologicalSorter
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
      parent_id TEXT REFERENCES tasks(id),
      design_gate_required INTEGER NOT NULL DEFAULT 0,
      design_task_id TEXT REFERENCES tasks(id),
      design_waiver TEXT NOT NULL DEFAULT '',
      CHECK (status IN ('queued','running','awaiting_review','awaiting_approval',
                        'completed','failed','cancelled'))
    );
    CREATE TABLE IF NOT EXISTS runs (
      id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
      profile TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
      exit_code INTEGER, status TEXT NOT NULL, prompt_path TEXT,
      log_path TEXT, workspace TEXT, error TEXT
    );
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
      name TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('active','closed')),
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS session_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL REFERENCES sessions(id),
      kind TEXT NOT NULL, actor TEXT NOT NULL, message TEXT NOT NULL,
      evidence TEXT NOT NULL DEFAULT '[]', at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      at TEXT NOT NULL, task_id TEXT NOT NULL REFERENCES tasks(id),
      event TEXT NOT NULL, actor TEXT NOT NULL, detail TEXT NOT NULL
    );
    """)
    # Upgrade pre-v0.3 databases without touching task history.
    if "parent_id" not in {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}:
        conn.execute("ALTER TABLE tasks ADD COLUMN parent_id TEXT REFERENCES tasks(id)")
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
    if "design_gate_required" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN design_gate_required INTEGER NOT NULL DEFAULT 0")
    if "design_task_id" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN design_task_id TEXT REFERENCES tasks(id)")
    if "design_waiver" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN design_waiver TEXT NOT NULL DEFAULT ''")
    if "readiness_scope" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN readiness_scope TEXT NOT NULL DEFAULT '{\"kind\":\"implementation\"}'")
    if "max_attempts" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN max_attempts INTEGER NOT NULL DEFAULT 3")
    run_columns = {row["name"] for row in conn.execute("PRAGMA table_info(runs)")}
    if "cancel_requested" not in run_columns:
        conn.execute("ALTER TABLE runs ADD COLUMN cancel_requested INTEGER NOT NULL DEFAULT 0")
    try:
        yield conn
    finally:
        conn.close()
        from .memory import sync_after_state_change
        sync_after_state_change(project)


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
    task["design_gate_required"] = bool(task.get("design_gate_required", 0))
    return task


def task(conn, task_id):
    return as_dict(conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())


def list_tasks(conn):
    return [as_dict(x) for x in conn.execute("SELECT * FROM tasks ORDER BY created_at,id")]


def validate_completion_graph(conn, task_id, depends, parent_id):
    """Include the implicit requirement that a parent waits for its children."""
    graph = TopologicalSorter()
    for item in list_tasks(conn):
        graph.add(item['id'], *item['dependencies'])
        if item['parent_id']:
            graph.add(item['parent_id'], item['id'])
    graph.add(task_id, *depends)
    if parent_id:
        graph.add(parent_id, task_id)
    try:
        graph.prepare()
    except CycleError as exc:
        cycle = ' -> '.join(exc.args[1])
        raise ValueError(f"Task dependency/delegation cycle: {cycle}") from exc


def add_task(conn, project, task_id, title, role, skill, acceptance, depends=(), context=(), approval=False, parent_id=None, design_task_id=None, design_waiver="", inception_step=None, spike_reason="", spike_scope="", spike_hours=24, max_attempts=3):
    if not TASK_ID.fullmatch(task_id) or len(task_id) > 80:
        raise ValueError("Task ID must be uppercase alphanumeric with hyphens (e.g. API-001)")
    if not title.strip() or not acceptance.strip():
        raise ValueError("Title and explicit acceptance criteria are required")
    if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
        raise ValueError("max_attempts must be an integer from 1 to 10")
    base = Path(project).resolve()
    if not (base / ".uasef" / "roles" / f"{role}.md").is_file():
        raise ValueError(f"Unknown role {role}")
    if not (base / ".agents" / "skills" / skill / "SKILL.md").is_file():
        raise ValueError(f"Unknown skill {skill}")
    depends, context = list(dict.fromkeys(depends)), list(dict.fromkeys(context))
    design_waiver = design_waiver.strip() if isinstance(design_waiver, str) else ""
    design_gate_required = role == "frontend-engineer"
    if design_gate_required:
        if design_task_id and design_waiver:
            raise ValueError("Choose --design-task or --design-waiver, not both")
        if design_task_id:
            design_task = task(conn, design_task_id)
            if design_task["role"] != "ux-designer" or not design_task["needs_approval"]:
                raise ValueError("--design-task must identify a UX task created with --approval-required")
            if design_task_id not in depends:
                depends.append(design_task_id)
        elif not 15 <= len(design_waiver) <= 500:
            raise ValueError("Frontend tasks need --design-task UX-ID or a 15-500 character --design-waiver reason")
    elif design_task_id or design_waiver:
        raise ValueError("--design-task and --design-waiver are only valid for frontend-engineer tasks")
    if task_id in depends:
        raise ValueError("Task may not depend on itself")
    if parent_id is not None:
        if parent_id == task_id:
            raise ValueError("A task cannot delegate to itself")
        parent = task(conn, parent_id)
        if parent["status"] in TERMINAL:
            raise ValueError("Cannot delegate from a closed task")
        depth, ancestor = 0, parent
        while ancestor["parent_id"] is not None:
            depth += 1
            ancestor = task(conn, ancestor["parent_id"])
        if depth >= 3:
            raise ValueError("Delegation depth limit of 3 exceeded")
    for d in depends:
        task(conn, d)  # Dependencies must exist; combined cycles are checked below.
    from .executor import safe_document
    for filename in context:
        safe_document(base, filename)
    from . import readiness
    execution_scope = readiness.scope(inception_step, spike_reason, spike_scope, spike_hours)
    if inception_step:
        error = readiness.blocked(base, {"readiness_scope": json.dumps(execution_scope), "role": role, "skill": skill})
        if error:
            raise ValueError(error)
    t = timestamp()
    conn.execute("BEGIN IMMEDIATE")
    try:
        validate_completion_graph(conn, task_id, depends, parent_id)
        if parent_id and task(conn, parent_id)["status"] in TERMINAL:
            raise ValueError("Cannot delegate from a closed task")
        conn.execute("INSERT INTO tasks(id,title,role,skill,acceptance,context_paths,dependencies,needs_approval,created_at,updated_at,parent_id,design_gate_required,design_task_id,design_waiver) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (task_id,title,role,skill,acceptance,json.dumps(context),json.dumps(depends),int(approval),t,t,parent_id,int(design_gate_required),design_task_id,design_waiver))
        audit(conn, task_id, "created", detail=f"depends={depends}; approval={approval}; parent={parent_id}; design_task={design_task_id or ''}; design_waiver={design_waiver}")
        conn.execute("UPDATE tasks SET readiness_scope=? WHERE id=?", (json.dumps(execution_scope), task_id))
        conn.execute("UPDATE tasks SET max_attempts=? WHERE id=?", (max_attempts, task_id))
        audit(conn, task_id, "readiness_scope", detail=json.dumps(execution_scope))
        audit(conn, task_id, "attempt_limit", detail=str(max_attempts))
        if parent_id:
            audit(conn, parent_id, "delegated", detail=f"child={task_id}; role={role}")
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Task already exists or violates constraints: {task_id}") from e
    except Exception:
        conn.rollback()
        raise
    return task(conn, task_id)


def eligible(conn, row):
    row = dict(row)
    if row["status"] != "queued" or row.get("attempts", 0) >= row.get("max_attempts", 3):
        return False
    task_data = dict(row)
    from . import readiness
    if readiness.blocked(readiness.project_for(conn), task_data):
        return False
    if task_data.get("design_gate_required"):
        design_task_id = task_data.get("design_task_id")
        waiver = task_data.get("design_waiver", "")
        if design_task_id:
            design = task(conn, design_task_id)
            if design["role"] != "ux-designer" or not design["needs_approval"] or design["status"] != "completed":
                return False
        elif not waiver:
            return False
    return all(task(conn, d)["status"] == "completed" for d in row["dependencies"])


def blocked_reason(conn, task_data):
    if task_data.get("attempts", 0) >= task_data.get("max_attempts", 3):
        return "Task attempt limit reached; create a newly scoped task after inspecting prior outcomes"
    from . import readiness
    return readiness.blocked(readiness.project_for(conn), task_data) or "Task is not ready (status, dependencies or design gate)"


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
            raise ValueError(blocked_reason(conn, t))
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
        cancelled = conn.execute("SELECT cancel_requested FROM runs WHERE id=?", (run_id,)).fetchone()
        outcome = "awaiting_review" if exit_code == 0 else "failed"
        if not error.startswith("Cleanup uncertain") and (
                (cancelled and cancelled[0]) or (exit_code == 130 and error.startswith("Cancellation"))):
            outcome = "cancelled"
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


def incomplete_children(conn, task_id):
    return [r["id"] for r in conn.execute("SELECT id FROM tasks WHERE parent_id=? AND status != 'completed' ORDER BY id", (task_id,))]


def verify(conn, project, task_id, reviewer, evidence, verification=None):
    from .verification import gate
    receipt_hash = gate(project, verification)
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
        remaining = incomplete_children(conn, task_id)
        if remaining:
            raise ValueError(f"Delegated tasks must complete before parent review: {', '.join(remaining)}")
        last = conn.execute("SELECT profile FROM runs WHERE task_id=? ORDER BY started_at DESC,id DESC LIMIT 1",(task_id,)).fetchone()
        manual = conn.execute("SELECT actor FROM audit WHERE task_id=? AND event='manual_submitted' ORDER BY id DESC LIMIT 1",(task_id,)).fetchone()
        if (last and reviewer.casefold() == last["profile"].casefold()) or (manual and reviewer.casefold() == manual["actor"].casefold()):
            raise ValueError("The execution profile or submitting actor cannot claim independent review")
        status = "awaiting_approval" if t["needs_approval"] else "completed"
        conn.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?",(status,timestamp(),task_id))
        audit(conn,task_id,"verified",actor=reviewer,detail=json.dumps(evidence))
        if verification:
            audit(conn, task_id, "verification_receipt", actor=reviewer,
                  detail=json.dumps({"id": verification, "sha256": receipt_hash}))
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
            raise ValueError(blocked_reason(conn, t))
        conn.execute("UPDATE tasks SET status='awaiting_review',updated_at=? WHERE id=?",(timestamp(),task_id))
        conn.execute("UPDATE tasks SET attempts=attempts+1 WHERE id=?", (task_id,))
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
        remaining = incomplete_children(conn, task_id)
        if remaining:
            raise ValueError(f"Delegated tasks still incomplete: {', '.join(remaining)}")
        conn.execute("UPDATE tasks SET status='completed',updated_at=? WHERE id=?",(timestamp(),task_id))
        audit(conn,task_id,"approved",actor=actor,detail=note)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def retry(conn, task_id, actor, inspect_note=""):
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn,task_id)
        from .worker_lock import active
        from .readiness import project_for
        if active(project_for(conn), task_id):
            raise ValueError("A managed worker is still active; wait for cancellation cleanup")
        if t["attempts"] >= t["max_attempts"]:
            raise ValueError("Task attempt limit reached")
        latest = conn.execute("SELECT status,error FROM runs WHERE task_id=? ORDER BY rowid DESC LIMIT 1", (task_id,)).fetchone()
        if latest and (latest["status"] == "interrupted" or "Cleanup uncertain" in (latest["error"] or "")):
            if not 15 <= len(inspect_note.strip()) <= 1000:
                raise ValueError("Inspect external workers and side effects, then provide --inspect-note (15-1000 characters)")
        if t["status"] != "failed":
            raise ValueError("Only failed tasks can be retried; running tasks require lease recovery")
        conn.execute("UPDATE tasks SET status='queued',updated_at=? WHERE id=?",(timestamp(),task_id))
        audit(conn,task_id,"retry",actor=actor,detail=inspect_note)
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
            from .worker_lock import active
            from .readiness import project_for
            if active(project_for(conn), task_id):
                continue
            conn.execute("UPDATE tasks SET status='failed',lease_token=NULL,lease_until=NULL,updated_at=? WHERE id=?",(timestamp(),task_id))
            conn.execute("UPDATE runs SET status='interrupted',finished_at=?,error='Lease expired; verify external process stopped before retry' WHERE task_id=? AND status='running'",(timestamp(),task_id))
            audit(conn,task_id,"lease_expired",actor=actor,detail="Marked failed; inspect worker before retry")
            recovered.append(task_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return recovered


def cancel_requested(project, run_id):
    with closing(sqlite3.connect(database_path(project), timeout=15)) as conn:
        row = conn.execute("SELECT cancel_requested FROM runs WHERE id=?", (run_id,)).fetchone()
        return bool(row and row[0])


def cancel(conn, task_id, actor="operator"):
    conn.execute("BEGIN IMMEDIATE")
    try:
        t = task(conn, task_id)
        if t["status"] in TERMINAL:
            raise ValueError("Task is already closed")
        if t["status"] == "running":
            conn.execute("UPDATE runs SET cancel_requested=1 WHERE task_id=? AND status='running'", (task_id,))
            result = "cancellation requested"
        else:
            conn.execute("UPDATE tasks SET status='cancelled',updated_at=? WHERE id=?", (timestamp(), task_id))
            result = "cancelled"
        audit(conn, task_id, "cancel_requested", actor=actor, detail=result)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise

"""Durable, explicit session checkpoints and portable handoffs.

Sessions preserve *declared* work state, not private model reasoning or hidden
conversations. Session metadata is local and is not an authentication system.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import uuid

from . import orchestrator as o
from .executor import safe_document

SESSION_ID = re.compile(r"^[a-f0-9]{32}$")
MAX_MESSAGE = 6000


def session(conn, identifier):
    if not SESSION_ID.fullmatch(identifier):
        raise ValueError("Invalid session ID")
    row = conn.execute("SELECT * FROM sessions WHERE id=?", (identifier,)).fetchone()
    if row is None:
        raise ValueError("Unknown session")
    return dict(row)


def start(conn, task_id, name, actor="operator"):
    o.task(conn, task_id)
    if not (1 <= len(name.strip()) <= 120):
        raise ValueError("Session name must contain 1–120 characters")
    sid = uuid.uuid4().hex
    with conn:
        conn.execute("INSERT INTO sessions(id,task_id,name,status,created_at,updated_at) VALUES(?,?,?,'active',?,?)",
                     (sid, task_id, name.strip(), o.timestamp(), o.timestamp()))
        _event(conn, sid, "session_started", actor, f"Session started for {task_id}", [])
        o.audit(conn, task_id, "session_started", actor, sid)
    return session(conn, sid)


def _event(conn, sid, kind, actor, message, evidence):
    if not isinstance(message, str) or not (1 <= len(message.strip()) <= MAX_MESSAGE):
        raise ValueError(f"Event message must be 1–{MAX_MESSAGE} characters")
    if not actor or len(actor.strip()) > 120:
        raise ValueError("Actor must contain 1–120 characters")
    conn.execute("INSERT INTO session_events(session_id,kind,actor,message,evidence,at) VALUES(?,?,?,?,?,?)",
                 (sid, kind, actor.strip(), message.strip(), json.dumps(evidence), o.timestamp()))
    conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (o.timestamp(), sid))


def record(conn, project, sid, kind, actor, message, evidence=()):
    if kind not in ("note", "checkpoint", "runner_started", "runner_finished"):
        raise ValueError("Unsupported event type")
    paths = list(dict.fromkeys(evidence))
    if len(paths) > 15:
        raise ValueError("Maximum 15 evidence paths per event")
    for path in paths:
        safe_document(project, path)
    with conn:
        current = session(conn, sid)
        if current["status"] != "active":
            raise ValueError("Closed sessions cannot be modified")
        _event(conn, sid, kind, actor, message, paths)
        o.audit(conn, current["task_id"], f"session_{kind}", actor, sid)


def close(conn, sid, actor, summary):
    with conn:
        current = session(conn, sid)
        if current["status"] != "active":
            raise ValueError("Session already closed")
        _event(conn, sid, "session_closed", actor, summary, [])
        conn.execute("UPDATE sessions SET status='closed' WHERE id=?", (sid,))
        o.audit(conn, current["task_id"], "session_closed", actor, sid)


def list_sessions(conn, task_id=None):
    if task_id:
        o.task(conn, task_id)
        rows = conn.execute("SELECT * FROM sessions WHERE task_id=? ORDER BY created_at DESC,id", (task_id,))
    else:
        rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC,id")
    return [dict(r) for r in rows]


def events(conn, sid, limit=20):
    session(conn, sid)
    if not (1 <= limit <= 100):
        raise ValueError("Event limit must be 1–100")
    rows = conn.execute("SELECT * FROM (SELECT * FROM session_events WHERE session_id=? ORDER BY id DESC LIMIT ?) ORDER BY id", (sid, limit))
    return [{**dict(x), "evidence": json.loads(x["evidence"])} for x in rows]


def context(conn, sid, limit=12):
    s = session(conn, sid)
    t = o.task(conn, s["task_id"])
    notes = events(conn, sid, limit=limit)
    lines = [f"# UASEF Session Handoff — {s['name']}", "",
             f"Session: `{sid}`", f"Status: {s['status']}",
             f"Task: `{t['id']}` — {t['title']}", f"Task state: `{t['status']}`",
             f"Agent role: `{t['role']}`; skill: `{t['skill']}`", "",
             "## Acceptance criteria", t["acceptance"], "",
             "## Session checkpoints and notes (not verified facts)"]
    for e in notes:
        lines += [f"- {e['at']} [{e['kind']}] {e['actor']}: {e['message']}"]
        if e["evidence"]:
            lines += [f"  Evidence paths: {', '.join(e['evidence'])}"]
    lines += ["", "## Successor instructions",
              "1. Read project AGENTS.md, role/skill documents and approved specifications.",
              "2. Verify working tree/commit, real files, and test results; do not trust notes as proof.",
              "3. Continue only within approved task scope. Never self-approve review or release.",
              "4. Record new findings with `uasef session checkpoint`.", ""]
    return "\n".join(lines)


def export(conn, project, sid):
    content = context(conn, sid)
    root = Path(project).resolve() / ".uasef" / "sessions" / sid
    root.mkdir(parents=True, exist_ok=True)
    out = root / "handoff.md"
    out.write_text(content, encoding="utf-8")
    return out

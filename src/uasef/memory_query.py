"""Derived full-text index and deterministic history inspection, no model service."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from . import memory as m


def search(project, query, limit=20, rebuild=False):
    if not query.strip() or not 1 <= limit <= 100:
        raise ValueError("Search requires text and a limit between 1 and 100")
    root = Path(project).resolve()
    target = root / ".uasef/memory-search.sqlite3"
    if target.is_symlink() or not target.resolve().is_relative_to(root):
        raise ValueError("Unsafe search cache path")
    target.parent.mkdir(parents=True, exist_ok=True)
    paths = sorted((m.directory(root) / "records").glob("MEM-*.json"))
    with closing(sqlite3.connect(target)) as conn:
        conn.execute("PRAGMA trusted_schema=OFF")
        conn.execute("CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY,signature TEXT NOT NULL)")
        try:
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(id UNINDEXED,title,text,kind UNINDEXED,task UNINDEXED)")
        except sqlite3.OperationalError as exc:
            raise ValueError("This Python SQLite build needs FTS5 for indexed search; use memory list --search instead") from exc
        known = dict(conn.execute("SELECT id,signature FROM files"))
        present = set()
        for path in paths:
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError("Unsafe memory path")
            present.add(path.stem)
            stat = path.stat()
            signature = f"{stat.st_mtime_ns}:{stat.st_size}"
            if not rebuild and known.get(path.stem) == signature:
                continue
            row = m._json(path)
            m.validate_record(row, path.stem)
            conn.execute("DELETE FROM documents WHERE id=?", (row["id"],))
            conn.execute("INSERT INTO documents VALUES(?,?,?,?,?)", (row["id"], row["title"], row["text"], row["kind"], row["task"]))
            conn.execute("INSERT OR REPLACE INTO files VALUES(?,?)", (row["id"], signature))
        for identifier in known.keys() - present:
            conn.execute("DELETE FROM documents WHERE id=?", (identifier,))
            conn.execute("DELETE FROM files WHERE id=?", (identifier,))
        conn.commit()
        # Treat user input as terms, not FTS query syntax or SQL.
        expression = " AND ".join('"' + term.replace('"', '""') + '"' for term in query.split())
        rows = conn.execute("SELECT id,title,kind,task,snippet(documents,2,'[',']','...',24) FROM documents WHERE documents MATCH ? ORDER BY bm25(documents),id LIMIT ?", (expression, limit))
        return [dict(zip(("id", "title", "kind", "task", "excerpt"), row)) for row in rows]


def timeline(project, task=None):
    rows = m.records(project)
    superseded = {r["supersedes"] for r in rows if r["supersedes"]}
    return [{**{k: r[k] for k in ("id", "at", "kind", "title", "claim", "actor", "task", "commit", "supersedes", "links")},
             "current": r["id"] not in superseded} for r in rows
            if r["kind"] in ("idea", "requirement", "decision", "preference", "verification") and (not task or r["task"] == task)]


def conflicts(project):
    rows = m.records(project)
    by_id = {r["id"]: r for r in rows}
    children = {}
    issues = []
    for row in rows:
        parent = row["supersedes"]
        if parent:
            children.setdefault(parent, []).append(row["id"])
        for link in row["links"] + ([parent] if parent else []):
            if link not in by_id:
                issues.append({"kind": "missing_reference", "records": [row["id"], link]})
        seen = set()
        current = row["id"]
        while current in by_id and current not in seen:
            seen.add(current)
            current = by_id[current]["supersedes"]
        if current in seen:
            issue = {"kind": "supersession_cycle", "records": sorted(seen)}
            if issue not in issues:
                issues.append(issue)
    for parent, ids in children.items():
        if len(ids) > 1:
            issues.append({"kind": "competing_revisions", "records": [parent] + sorted(ids)})
    groups = {}
    for row in rows:
        if row["id"] not in children and row["kind"] in ("decision", "preference"):
            groups.setdefault((row["kind"], row["title"].casefold().strip(), row["task"]), []).append(row)
    for group in groups.values():
        if len({r["text"].strip() for r in group}) > 1:
            issues.append({"kind": "possible_conflict_same_title", "records": [r["id"] for r in group]})
    return issues


def run(args):
    if args.query_action == "search":
        result = search(args.project, args.query, args.limit, args.rebuild)
    elif args.query_action == "timeline":
        if not 1 <= args.limit <= 1000 or args.offset < 0:
            raise ValueError("Timeline limit must be 1-1000 and offset nonnegative")
        result = timeline(args.project, args.task)[args.offset:args.offset + args.limit]
    else:
        result = conflicts(args.project)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def attach(actions):
    for name in ("search", "timeline", "conflicts"):
        p = actions.add_parser(name)
        p.add_argument("--project", default=".")
        p.set_defaults(func=run, query_action=name)
        if name == "search":
            p.add_argument("query")
            p.add_argument("--limit", type=int, default=20)
            p.add_argument("--rebuild", action="store_true")
        if name == "timeline":
            p.add_argument("--task")
            p.add_argument("--limit", type=int, default=100)
            p.add_argument("--offset", type=int, default=0)

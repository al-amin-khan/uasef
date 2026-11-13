"""Git-backed project memory commands."""
import json

from . import memory as m


def run(args):
    from .cli import load
    action = args.memory_action
    if action == "init":
        state = load(args.project)
        m.initialize(args.project, state["idea"])
    elif not (m.directory(args.project) / "project.json").is_file():
        raise ValueError("Run 'uasef memory init' or 'uasef upgrade' first")
    m.sync(args.project)
    if action == "add":
        row = m.add(args.project, args.kind, args.title, args.text, args.actor, args.claim,
                    args.link, args.task, args.evidence, args.commit, args.supersedes)
        print(row["id"])
    elif action == "brief":
        print(m.brief(args.project, args.task, args.limit))
    elif action in ("show", "trace", "list"):
        rows = m.trace(args.project, args.id) if action == "trace" else m.records(args.project)
        if action == "show":
            rows = [r for r in rows if r["id"] == args.id]
            if not rows:
                raise ValueError("Unknown memory ID")
        if action == "list":
            rows = [r for r in rows if (not args.kind or r["kind"] == args.kind)
                    and (not args.task or r["task"] == args.task)
                    and (not args.search or args.search.casefold() in json.dumps(r, ensure_ascii=False).casefold())]
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    elif action == "checkpoint":
        print(m.checkpoint(args.project, args.message, args.init_git))
    elif action == "validate":
        errors = m.validate(args.project)
        print("\n".join(errors) if errors else "Memory references and recorded evidence hashes match; tests were not rerun")
        return 1 if errors else 0
    else:
        print("Project memory synchronized")


def attach(sub):
    p = sub.add_parser("memory", help="Portable project memory and Git traceability")
    actions = p.add_subparsers(dest="memory_action", required=True)
    from .memory_query import attach as attach_query
    attach_query(actions)
    for name in ("init", "sync", "brief", "list", "show", "trace", "validate", "checkpoint", "add"):
        q = actions.add_parser(name)
        q.add_argument("--project", default=".")
        q.set_defaults(func=run)
        if name in ("show", "trace"):
            q.add_argument("id")
        if name in ("brief", "list", "add"):
            q.add_argument("--task")
        if name == "brief":
            q.add_argument("--limit", type=int, default=16)
        if name == "list":
            q.add_argument("--kind", choices=m.KINDS)
            q.add_argument("--search")
        if name == "checkpoint":
            q.add_argument("--message", required=True)
            q.add_argument("--init-git", action="store_true", help="Explicitly initialize Git if needed")
        if name == "add":
            q.add_argument("kind", choices=m.KINDS[:8])
            q.add_argument("--title", required=True)
            q.add_argument("--text", required=True)
            q.add_argument("--actor", default="operator")
            q.add_argument("--claim", choices=m.CLAIMS, default="declared")
            q.add_argument("--link", action="append", default=[])
            q.add_argument("--supersedes")
            q.add_argument("--evidence", action="append", default=[])
            q.add_argument("--commit", help="Existing commit SHA implementing/verifying this record")

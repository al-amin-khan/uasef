"""User-facing persistent session and routing commands."""
from __future__ import annotations

import json

from . import orchestrator as o
from . import sessions
from . import routing
from .executor import load_runner_config


def start(args):
    with o.db(args.project) as conn:
        s = sessions.start(conn, args.task, args.name, actor=args.actor)
    print(f"Started session {s['id']} for {s['task_id']}")


def list_(args):
    with o.db(args.project) as conn:
        all_ = sessions.list_sessions(conn,args.task)
    for s in all_:
        print(f"{s['id']} {s['status']:8} {s['task_id']:18} {s['name']}")
    if not all_:
        print("No sessions")


def show(args):
    with o.db(args.project) as conn:
        s = sessions.session(conn,args.id)
        events = sessions.events(conn,args.id,args.limit)
    print(json.dumps({"session":s,"events":events},indent=2))


def note(args):
    with o.db(args.project) as conn:
        sessions.record(conn,args.project,args.id,"checkpoint" if args.checkpoint else "note",args.actor,args.message,args.evidence)
    print(f"Recorded {'checkpoint' if args.checkpoint else 'note'} for session {args.id}")


def handoff(args):
    with o.db(args.project) as conn:
        dest=sessions.export(conn,args.project,args.id)
    print(f"Handoff written: {dest}")


def close(args):
    with o.db(args.project) as conn:
        sessions.close(conn,args.id,args.actor,args.summary)
    print(f"Closed session {args.id}")


def route(args):
    with o.db(args.project) as conn:
        t = o.task(conn,args.task)
    config = load_runner_config(args.project)
    choices = routing.evaluate(config,t)
    print(json.dumps({"task":args.task,"route":choices},indent=2))
    if choices:
        print("Selection: " + (next((x['profile'] for x in choices if x['eligible']),"none")))
    else:
        print("No candidates configured")


def attach(sub):
    parent=sub.add_parser("session",help="Persistent, auditable agent session checkpoints")
    actions=parent.add_subparsers(dest="session_action",required=True)
    q=actions.add_parser("start");q.add_argument("--task",required=True);q.add_argument("--name",required=True);q.add_argument("--actor",default="operator");q.set_defaults(func=start)
    q=actions.add_parser("list");q.add_argument("--task");q.set_defaults(func=list_)
    q=actions.add_parser("show");q.add_argument("id");q.add_argument("--limit",type=int,default=20);q.set_defaults(func=show)
    for cmd,is_checkpoint in (("note",False),("checkpoint",True)):
        q=actions.add_parser(cmd);q.add_argument("id");q.add_argument("--actor",default="operator")
        q.add_argument("--message",required=True);q.add_argument("--evidence",action="append",default=[])
        q.set_defaults(func=note,checkpoint=is_checkpoint)
    q=actions.add_parser("handoff");q.add_argument("id");q.set_defaults(func=handoff)
    q=actions.add_parser("close");q.add_argument("id");q.add_argument("--actor",default="operator");q.add_argument("--summary",required=True);q.set_defaults(func=close)
    for q in actions.choices.values():q.add_argument("--project",default=".")
    q=sub.add_parser("route",help="Explain runner selection for a task without executing")
    q.add_argument("--task",required=True);q.add_argument("--project",default=".");q.set_defaults(func=route)

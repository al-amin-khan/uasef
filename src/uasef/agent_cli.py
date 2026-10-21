"""CLI actions for v0.2 orchestration.  Kept separate from v0.1 inception CLI."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path

from . import executor as ex
from . import orchestrator as orch


def add(args):
    with orch.db(args.project) as conn:
        t = orch.add_task(conn,args.project,args.id,args.title,args.role,args.skill,
                          args.acceptance,args.depends,args.context,args.approval_required,args.parent)
    print(f"Created {t['id']} [{t['status']}] role={t['role']} skill={t['skill']}")


def status(args):
    with orch.db(args.project) as conn:
        rows=orch.list_tasks(conn)
        for t in rows:
            flag = " [READY]" if orch.eligible(conn,t) else ""
            print(f"{t['id']:20} {t['status']:19} {t['role']:22} {t['title']}{flag}")
        if not rows:
            print("No execution tasks yet. Use: uasef task add --help")


def details(args):
    with orch.db(args.project) as conn:
        t = orch.task(conn,args.id)
        logs=[dict(r) for r in conn.execute("SELECT id,profile,started_at,finished_at,exit_code,status,workspace,error FROM runs WHERE task_id=? ORDER BY started_at DESC",(args.id,))]
        events=[dict(r) for r in conn.execute("SELECT at,event,actor,detail FROM audit WHERE task_id=? ORDER BY id",(args.id,))]
        print(json.dumps({"task":t,"runs":logs,"audit":events},indent=2))


def verify(args):
    with orch.db(args.project) as conn:
        result=orch.verify(conn,args.project,args.id,args.reviewer,args.evidence)
    print(f"Review recorded: {args.id} -> {result}. Local reviewer identity is not authenticated.")


def submit(args):
    with orch.db(args.project) as conn:
        orch.submit_manual(conn,args.project,args.id,args.actor,args.evidence)
    print(f"Manual task {args.id} submitted for independent review. This is not verification.")


def approve(args):
    with orch.db(args.project) as conn:
        orch.approve(conn,args.id,args.actor,args.note)
    print(f"Approval recorded: {args.id} completed. For enforceable human approvals use protected branches and environment controls.")


def retry(args):
    with orch.db(args.project) as conn:
        orch.retry(conn,args.id,args.actor)
    print(f"Task {args.id} requeued.")


def recover(args):
    with orch.db(args.project) as conn:
        rows = orch.recover_expired(conn,args.actor)
    print(f"Expired running leases marked failed: {', '.join(rows) if rows else '(none)'}")
    if rows:
        print("Inspect external workers and worktrees before retrying; lease expiry does not kill orphan processes.")


def profiles(args):
    for k,v in ex.load_profiles(args.project).items():
        print(f"{k:20} {v.get('type','INVALID')}")


def tree(args):
    with orch.db(args.project) as conn:
        tasks=orch.list_tasks(conn)
    def walk(parent,depth=0):
        for t in tasks:
            if t["parent_id"] == parent:
                print("  "*depth+f"{t['id']} [{t['status']}] {t['title']}")
                walk(t["id"],depth+1)
    walk(None)


def _dispatch(project, task_id, profile_name, execute, worktree=False, session_id=None):
    root=Path(project).resolve()
    from . import routing, sessions
    config=ex.load_runner_config(root)
    settings=config["profiles"]
    with orch.db(root) as conn:
        t=orch.task(conn,task_id)
        if session_id is not None:
            active=sessions.session(conn,session_id)
            if active["status"] != "active" or active["task_id"] != task_id:
                raise ValueError("Session must be active and belong to this task")
    if profile_name == "auto":
        profile_name=routing.select(config,t)
    if profile_name not in settings:
        raise ValueError(f"Unknown runner profile '{profile_name}'; configure .uasef/runners.json")
    profile=settings[profile_name]
    if not isinstance(profile,dict):
        raise ValueError("Invalid runner profile")
    if profile.get("enabled",True) is not True:
        raise ValueError("Runner profile is disabled")
    if profile.get("roles") is not None and t["role"] not in profile["roles"]:
        raise ValueError("Runner profile does not permit this role")
    if profile.get("skills") is not None and t["skill"] not in profile["skills"]:
        raise ValueError("Runner profile does not permit this skill")
    with orch.db(root) as conn:
        if not orch.eligible(conn,t):
            raise ValueError(f"Task {task_id} is not ready")
        # Prevalidate context and command before claiming the task.
        ex.build_prompt(root,t)
        if profile.get("type") == "manual":
            if execute:
                raise ValueError("Manual mode cannot --execute")
            prompt=ex.prepare(root,t,f"manual-{task_id.lower()}")
            if session_id:
                with prompt.open("a",encoding="utf-8") as file:file.write("\n\n"+sessions.context(conn,session_id))
            return f"Manual prompt prepared: {prompt}. Task remains queued; agent work is not verified automatically."
        if not execute:
            prompt=ex.prepare(root,t,f"preview-{task_id.lower()}")
            if session_id:
                with prompt.open("a",encoding="utf-8") as file:file.write("\n\n"+sessions.context(conn,session_id))
            return f"Dry run only. Selected {profile_name}; prompt: {prompt}. Use --execute to opt into subprocess execution."
        timeout = ex.validate_profile(profile)
        run_id,token=orch.claim(conn,task_id,profile_name,lease_seconds=timeout+120)
    prompt_path=root / ".uasef" / "runs" / run_id / "prompt.md"
    log_path=prompt_path.parent / "runner.log"
    workspace=root
    code=127
    err=""
    try:
        prompt_path=ex.prepare(root,t,run_id)
        if session_id:
            with orch.db(root) as conn:
                with prompt_path.open("a",encoding="utf-8") as file:
                    file.write("\n\n"+sessions.context(conn,session_id))
                sessions.record(conn,root,session_id,"runner_started",profile_name,f"Runner started; run={run_id}")
        if worktree:
            workspace=ex.make_worktree(root,task_id,run_id)
        code,err=ex.execute(root,profile_name,profile,prompt_path,log_path,workspace,task_id)
    except Exception as exc:
        err=f"Dispatch error: {type(exc).__name__}: {exc}"
    with orch.db(root) as conn:
        result=orch.finish_run(conn,task_id,run_id,token,code,prompt_path,log_path,workspace,err)
        if session_id:
            try:
                sessions.record(conn,root,session_id,"runner_finished",profile_name,f"Runner {run_id}: exit={code}, status={result}; inspect run logs")
            except ValueError:
                # A session can be closed while an external process is running.
                # Its task/run outcome is still persisted in authoritative execution state.
                pass
    return (f"Task {task_id}: {result}; run={run_id}; exit={code}; workspace={workspace}; log={log_path}. "
            + (f"Error: {err}. " if err else "")
            + ("Requires independent review and test evidence before completion." if code==0 else "Inspect logs, then use 'uasef task retry' if appropriate."))


def dispatch(args):
    print(_dispatch(args.project,args.id,args.profile,args.execute,args.worktree,args.session))


def dispatch_ready(args):
    if args.jobs < 1 or args.limit < 1:
        raise ValueError("--jobs and --limit must be positive")
    if args.jobs > 1 and args.execute and not args.worktree:
        raise ValueError("Parallel execution requires --worktree to avoid workspace collisions")
    with orch.db(args.project) as conn:
        ready=orch.ready_tasks(conn)[:args.limit]
    if not ready:
        print("No ready tasks")
        return
    if args.jobs <= 1:
        for t in ready:
            print(_dispatch(args.project,t['id'],args.profile,args.execute,args.worktree))
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures=[pool.submit(_dispatch,args.project,t['id'],args.profile,args.execute,args.worktree) for t in ready]
            for f in as_completed(futures):
                print(f.result())


def attach(sub):
    tasks=sub.add_parser("task",help="v0.2 durable agent execution tasks")
    actions=tasks.add_subparsers(dest="task_action",required=True)
    q=actions.add_parser("add"); q.add_argument("id"); q.add_argument("--title",required=True)
    q.add_argument("--role",required=True);q.add_argument("--skill",required=True)
    q.add_argument("--acceptance",required=True)
    q.add_argument("--depends",action="append",default=[])
    q.add_argument("--context",action="append",default=[])
    q.add_argument("--approval-required",action="store_true")
    q.add_argument("--parent",help="Delegating parent task; child must complete before parent review")
    q.set_defaults(func=add)
    q=actions.add_parser("delegate",help="Create a scoped child task under a parent")
    q.add_argument("id");q.add_argument("--parent",required=True);q.add_argument("--title",required=True)
    q.add_argument("--role",required=True);q.add_argument("--skill",required=True)
    q.add_argument("--acceptance",required=True);q.add_argument("--depends",action="append",default=[])
    q.add_argument("--context",action="append",default=[]);q.add_argument("--approval-required",action="store_true")
    q.set_defaults(func=add)
    for name,fn in (("list",status),("tree",tree),("show",details),("verify",verify),("submit",submit),("approve",approve),("retry",retry),("recover",recover)):
        q=actions.add_parser(name)
        if name in ("show","verify","submit","approve","retry"):q.add_argument("id")
        if name=="verify":
            q.add_argument("--reviewer",required=True);q.add_argument("--evidence",action="append",required=True)
        if name=="submit":
            q.add_argument("--actor",required=True);q.add_argument("--evidence",action="append",required=True)
        if name=="approve":
            q.add_argument("--actor",required=True);q.add_argument("--note",required=True)
        if name in ("retry","recover"):q.add_argument("--actor",default="operator")
        q.set_defaults(func=fn)
    for q in actions.choices.values():
        q.add_argument("--project",default=".")
    for name,fn in (("dispatch",dispatch),("dispatch-ready",dispatch_ready)):
        q=sub.add_parser(name,help="Prepare prompt or opt into explicit configured external runner execution")
        if name=="dispatch":q.add_argument("id")
        else:
            q.add_argument("--limit",type=int,default=10)
            q.add_argument("--jobs",type=int,default=1)
        q.add_argument("--profile",default="manual");q.add_argument("--execute",action="store_true")
        q.add_argument("--worktree",action="store_true");q.add_argument("--project",default=".")
        if name == "dispatch": q.add_argument("--session",help="Active session ID for checkpoint context")
        q.set_defaults(func=fn)
    q=sub.add_parser("runners",help="List installed runner profiles")
    q.add_argument("--project",default=".");q.set_defaults(func=profiles)

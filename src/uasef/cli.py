"""Offline, standard-library-only UASEF CLI.

This CLI tracks task transitions and checks basic artifact readiness. It does not
execute or authenticate AI agents, prove content quality, or deploy anything.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys

VERSION = "0.3.0"
TASK_RE = re.compile(r"^INIT-0(?:0[1-9]|1[0-6])$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SKILL_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_TOKENS = ("TODO:", "{{", "[FILL IN]", "PLACEHOLDER:")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def framework_root():
    # Source checkout and editable install are supported. Release packaging
    # should include resources with package_data if distributing wheels.
    root = Path(__file__).resolve().parents[2]
    if not (root / "workflows" / "inception.json").is_file():
        raise RuntimeError("Framework resources not found. Run from a source checkout or editable install.")
    return root


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def state_path(project):
    return Path(project).resolve() / ".uasef" / "state.json"


def load(project):
    target = state_path(project)
    if not target.is_file():
        raise ValueError(f"Not a UASEF project: {target.parent}. Run 'uasef init <path>' first.")
    return read_json(target)


def save(project, state):
    state["updated_at"] = now()
    write_json(state_path(project), state)


def log(state, action, task=None, note=""):
    state.setdefault("audit", []).append({"at": now(), "action": action, "task": task, "note": note})


def step(state, task_id):
    for item in state["tasks"]:
        if item["id"] == task_id:
            return item
    raise ValueError(f"Unknown task {task_id}; use 'uasef status'.")


def ready(state, item):
    return all(step(state, dep)["status"] == "completed" for dep in item["depends_on"])


def safe_relative(target, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe relative path: {relative}")
    return target / path


def write_if_missing(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def copy_if_missing(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)


def install_adapter(root, project, adapter):
    # Canonical skill copies are installed in .agents/skills. An adapter copies
    # them to the discovery location documented by the selected coding tool.
    if adapter in ("codex", "all"):
        for skill in sorted((root / "skills").iterdir()):
            if skill.is_dir():
                for asset in skill.rglob("*"):
                    if asset.is_file():
                        copy_if_missing(asset, project / ".agents" / "skills" / skill.name / asset.relative_to(skill))
    if adapter in ("claude", "all"):
        for skill in sorted((root / "skills").iterdir()):
            if skill.is_dir():
                for asset in skill.rglob("*"):
                    if asset.is_file():
                        copy_if_missing(asset, project / ".claude" / "skills" / skill.name / asset.relative_to(skill))
        write_if_missing(project / "CLAUDE.md", "# Agent instructions\n\nRead [AGENTS.md](AGENTS.md), follow framework policies, and use project-local skills.\n")
    if adapter in ("copilot", "all"):
        write_if_missing(project / ".github" / "copilot-instructions.md", "Follow the repository [AGENTS.md](../../AGENTS.md), specifications and UASEF policies. Do not treat skills as executable guards.\n")
        for role in sorted((root / "agents").glob("*.md")):
            body = role.read_text(encoding="utf-8")
            copy_text = f"---\nname: {role.stem}\ndescription: UASEF {role.stem.replace('-', ' ')} specialist following repository governance.\n---\n\n" + body
            write_if_missing(project / ".github" / "agents" / (role.stem + ".agent.md"), copy_text)


def init(args):
    root = framework_root()
    p = Path(args.path).resolve()
    sp = state_path(p)
    if sp.exists():
        raise ValueError("Project already initialized; refusing to overwrite task state.")
    if p.exists() and any(p.iterdir()) and not args.existing:
        raise ValueError("Target is not empty. Pass --existing to add UASEF safely without overwriting files.")
    p.mkdir(parents=True, exist_ok=True)
    name = args.name or p.name
    idea = args.idea or "Not provided. Describe the problem during INIT-001."
    workflow = read_json(root / "workflows" / "inception.json")
    tasks = []
    for t in workflow["tasks"]:
        tasks.append({**t, "status": "pending", "started_at": None, "finished_at": None, "evidence": []})
        for output in t["outputs"]:
            src = safe_relative(root / "templates", output)
            if not src.is_file():
                raise ValueError(f"Missing template {src}")
            copy_if_missing(src, safe_relative(p, output))
    for source, dest in [("templates/AGENTS.md", "AGENTS.md"),
                         ("templates/README.project.md", "README.md")]:
        copy_if_missing(root / source, p / dest)
    # Keep human-readable metadata consistent with the machine-readable task state.
    project_yaml = p / "project.yaml"
    if not project_yaml.exists():
        project_yaml.write_text(
            "project:\n" +
            f"  name: {json.dumps(name, ensure_ascii=False)}\n" +
            f"  description: {json.dumps(idea, ensure_ascii=False)}\n" +
            "  lifecycle: inception\n  framework: uasef\n" +
            f"  framework_version: {json.dumps(VERSION)}\n" +
            "  stack: null\n  source_of_truth: docs/\n  task_state: .uasef/state.json\n",
            encoding="utf-8")
    intake = p / "docs" / "00-inception" / "idea-brief.md"
    if idea != "Not provided. Describe the problem during INIT-001.":
        with intake.open("a", encoding="utf-8") as f:
            f.write("\n## Original user idea (unverified intake)\n\n" + idea + "\n")
    # Project-local policies and role contracts are copies for portability.
    for policy in (root / "policies").glob("*.md"):
        copy_if_missing(policy, p / ".uasef" / "policies" / policy.name)
    for role in (root / "agents").glob("*.md"):
        copy_if_missing(role, p / ".uasef" / "roles" / role.name)
    # Canonical .agents/skills is always installed; other adapters optional.
    install_adapter(root, p, "codex")
    if args.adapter != "codex":
        install_adapter(root, p, args.adapter)
    state = {"schema_version": 1, "framework_version": VERSION, "name": name,
             "idea": idea, "created_at": now(), "updated_at": now(),
             "tasks": tasks, "audit": []}
    log(state, "init", note=f"adapter={args.adapter}")
    # Execution state is project-local and deliberately excluded from Git by default.
    write_if_missing(p / ".uasef" / "runners.json", (root / "templates" / "runners.json").read_text(encoding="utf-8"))
    write_if_missing(p / ".uasef" / ".gitignore", "orchestration.sqlite3*\nruns/\nworktrees/\nsessions/\n")
    save(p, state)
    print(f"Initialized {name} at {p}\nStart with: uasef next --project {p}")


def upgrade(args):
    """Install missing tools into an existing supported project without clobbering."""
    root = framework_root()
    p = Path(args.project).resolve()
    state = load(p)
    if state.get("framework_version") not in ("0.1.0", "0.2.0", "0.3.0"):
        raise ValueError("Unsupported source framework version; review upgrade manually")
    for policy in (root / "policies").glob("*.md"):
        copy_if_missing(policy, p / ".uasef" / "policies" / policy.name)
    for role in (root / "agents").glob("*.md"):
        copy_if_missing(role, p / ".uasef" / "roles" / role.name)
    install_adapter(root,p,"codex")
    if args.adapter != "codex":
        install_adapter(root,p,args.adapter)
    write_if_missing(p / ".uasef" / "runners.json", (root / "templates" / "runners.json").read_text(encoding="utf-8"))
    write_if_missing(p / ".uasef" / ".gitignore", "orchestration.sqlite3*\nruns/\nworktrees/\nsessions/\n")
    ignored=p / ".uasef" / ".gitignore"
    if "sessions/" not in ignored.read_text(encoding="utf-8").splitlines():
        with ignored.open("a", encoding="utf-8") as f: f.write("\nsessions/\n")
    state["framework_version"] = VERSION
    log(state, "framework_upgrade", note="New files copied without replacing customized agent instructions")
    save(p,state)
    print(f"Upgraded execution tools for {p} to UASEF {VERSION}. Existing role/policy files were not overwritten; reconcile changes manually.")


def status(args):
    state = load(args.project)
    print(f"{state['name']} | framework {state['framework_version']}")
    for item in state["tasks"]:
        dep = ",".join(item["depends_on"]) if item["depends_on"] else "-"
        suffix = " [READY]" if item["status"] == "pending" and ready(state, item) else ""
        print(f"{item['id']:8s} {item['status']:18s} {item['title']} (after {dep}){suffix}")


def next_tasks(args):
    state = load(args.project)
    for item in state["tasks"]:
        if item["status"] == "in_progress":
            print(f"CONTINUE {item['id']} {item['title']}: {', '.join(item['outputs'])}")
        if item["status"] == "awaiting_approval":
            print(f"APPROVAL {item['id']} {item['title']} (human review required)")
        if item["status"] == "pending" and ready(state, item):
            print(f"READY {item['id']} {item['title']} [role: {item['role']}]\n  Outputs: {', '.join(item['outputs'])}")


def start(args):
    state = load(args.project)
    item = step(state, args.id)
    if item["status"] != "pending":
        raise ValueError(f"Cannot start {item['id']}: {item['status']}")
    if not ready(state, item):
        raise ValueError(f"Dependencies incomplete: {', '.join(d for d in item['depends_on'] if step(state,d)['status']!='completed')}")
    item["status"] = "in_progress"
    item["started_at"] = now()
    log(state, "start", item["id"])
    save(args.project, state)
    print(f"Started {item['id']}. Agent role: {item['role']}. Required outputs:\n" + "\n".join(item["outputs"]))


def check_outputs(project, outputs):
    errors = []
    for rel in outputs:
        path = safe_relative(Path(project).resolve(), rel)
        if not path.is_file():
            errors.append(f"Missing: {rel}")
            continue
        data = path.read_text(encoding="utf-8")
        if len(data.strip()) < 100 or any(marker in data for marker in PLACEHOLDER_TOKENS):
            errors.append(f"Unfinished template: {rel}; replace TODO/placeholder instructions and provide substantive content")
    return errors


def complete(args):
    state = load(args.project)
    item = step(state, args.id)
    if item["status"] != "in_progress":
        raise ValueError("Only an in-progress task can be completed.")
    errors = check_outputs(args.project, item["outputs"])
    if errors:
        raise ValueError("\n".join(errors))
    for evidence in (args.evidence or []):
        if not safe_relative(Path(args.project).resolve(), evidence).is_file():
            raise ValueError(f"Evidence file not found: {evidence}")
    item["evidence"] = args.evidence or []
    if item["approval_required"]:
        item["status"] = "awaiting_approval"
        print(f"{item['id']} ready for human review. After reviewing artifacts: uasef approve {item['id']} --note 'reason'")
    else:
        item["status"] = "completed"
        item["finished_at"] = now()
        print(f"Completed {item['id']} (artifact presence verified; contents are NOT independently audited).")
    log(state, "complete", item["id"], note="artifact checks passed")
    save(args.project, state)


def approve(args):
    state = load(args.project)
    item = step(state, args.id)
    if item["status"] != "awaiting_approval":
        raise ValueError("Only tasks awaiting approval can be approved.")
    if len(args.note.strip()) < 10:
        raise ValueError("Provide a meaningful approval note (at least 10 characters).")
    item["status"] = "completed"
    item["finished_at"] = now()
    item["approval_note"] = args.note
    log(state, "human_approval_recorded", item["id"], args.note)
    save(args.project, state)
    print(f"Recorded approval for {item['id']} (local declaration; no user authentication).")


def validate(args):
    p = Path(args.project).resolve()
    state = load(p)
    errors = []
    root = framework_root()
    ids = [t["id"] for t in state["tasks"]]
    expected = read_json(root / "workflows" / "inception.json")
    if ids != [t["id"] for t in expected["tasks"]]:
        errors.append("Workflow task IDs differ from reference manifest")
    for t in state["tasks"]:
        if t["status"] in ("completed", "awaiting_approval"):
            errors.extend(check_outputs(p, t["outputs"]))
        for dep in t["depends_on"]:
            if dep not in ids:
                errors.append(f"Unknown dependency {dep} for {t['id']}")
    for f in (p / ".agents" / "skills").glob("*/SKILL.md"):
        txt = f.read_text(encoding="utf-8")
        m = re.match(r"\A---\nname:\s*([^\n]+)\ndescription:\s*([^\n]+)\n---\n", txt)
        if not m or not SKILL_RE.fullmatch(m.group(1).strip()) or m.group(1).strip() != f.parent.name:
            errors.append(f"Invalid skill metadata: {f}")
    if not list((p / ".agents" / "skills").glob("*/SKILL.md")):
        errors.append("No agent skills installed")
    if errors:
        print("Validation failed:\n" + "\n".join("- " + e for e in errors))
        return 1
    print("Structural validation passed. This does NOT certify research accuracy, security or software readiness.")
    return 0


def handoff(args):
    p = Path(args.project).resolve()
    state = load(p)
    summary = [f"# Model-agnostic handoff: {state['name']}", "", f"Framework: {state['framework_version']}",
               f"Generated: {now()}", "", "## Original idea", state["idea"], "",
               "## State (verify actual artifacts before acting)", ""]
    for t in state["tasks"]:
        summary.append(f"- {t['id']} **{t['status']}** {t['title']}; outputs: {', '.join(t['outputs'])}")
    from . import orchestrator as orch
    with orch.db(p) as conn:
        active = orch.list_tasks(conn)
        if active:
            summary.extend(["", "## v0.2 execution tasks (transactional state)", ""])
            for item in active:
                summary.append(f"- {item['id']} **{item['status']}** [{item['role']} / {item['skill']}]; acceptance: {item['acceptance']}; dependencies: {', '.join(item['dependencies']) or 'none'}")
                recent = conn.execute("SELECT id,profile,status,workspace,log_path FROM runs WHERE task_id=? ORDER BY started_at DESC LIMIT 1", (item['id'],)).fetchone()
                if recent:
                    summary.append(f"  - Last run: {recent['id']} ({recent['profile']}, {recent['status']}); workspace: {recent['workspace']}; log: {recent['log_path']}")
    summary.extend(["", "## Instructions for successor agent", "1. Read AGENTS.md and local policy files.",
                    "2. Verify repository HEAD, current branch, and the real files; do not trust this handoff alone.",
                    "3. Continue current or next eligible task; do not bypass approvals.",
                    "4. Cite evidence or say what has not been verified.", ""])
    out = p / ".uasef" / "handoff.md"
    out.write_text("\n".join(summary), encoding="utf-8")
    print(f"Wrote {out}")


def feature(args):
    p = Path(args.project).resolve()
    load(p)
    if not SLUG_RE.fullmatch(args.slug):
        raise ValueError("Feature slug must be kebab-case.")
    base = p / "specs" / "features" / args.slug
    if base.exists():
        raise ValueError("Feature exists; refusing to overwrite.")
    base.mkdir(parents=True)
    for name in ("proposal.md", "requirements.md", "design.md", "tasks.md", "verification.md"):
        (base / name).write_text(f"# {args.slug}: {name[:-3].replace('-', ' ').title()}\n\nTODO: Define scope, evidence, and criteria before implementation.\n", encoding="utf-8")
    print(f"Feature package created: {base}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="uasef", description="Portable AI engineering inception framework (local task state)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="Initialize a project without overwriting existing files")
    p.add_argument("path"); p.add_argument("--name"); p.add_argument("--idea")
    p.add_argument("--existing", action="store_true", help="Allow an existing nonempty project; never overwrite")
    p.add_argument("--adapter", choices=("codex", "claude", "copilot", "all"), default="all")
    p.set_defaults(func=init)
    for command, func in (("status",status),("next",next_tasks),("validate",validate),("handoff",handoff)):
        q = sub.add_parser(command)
        q.add_argument("--project", default=".")
        q.set_defaults(func=func)
    for command, func in (("start",start),("complete",complete),("approve",approve)):
        q = sub.add_parser(command); q.add_argument("id")
        q.add_argument("--project", default=".")
        if command == "complete": q.add_argument("--evidence", action="append")
        if command == "approve": q.add_argument("--note", required=True)
        q.set_defaults(func=func)
    q = sub.add_parser("upgrade", help="Install v0.3 framework files without overwriting customizations")
    q.add_argument("--project", default=".")
    q.add_argument("--adapter", choices=("codex","claude","copilot","all"), default="all")
    q.set_defaults(func=upgrade)
    q = sub.add_parser("feature", help="Start a feature specification package")
    q.add_argument("slug"); q.add_argument("--project", default=".")
    q.set_defaults(func=feature)
    from .agent_cli import attach
    from .session_cli import attach as attach_sessions
    attach(sub)
    attach_sessions(sub)
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        return int(result) if result is not None else 0
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

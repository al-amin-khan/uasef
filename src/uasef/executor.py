"""Prompt builder and opt-in execution adapters.

External commands run with the current user's privileges. A Git worktree isolates
Git changes only; it is NOT a filesystem, network, or OS security sandbox.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading

MAX_DOC_BYTES = 75000
MAX_CONTEXT_BYTES = 220000
_WORKTREE_LOCK = threading.Lock()


def safe_document(root, relative):
    base = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in ("..", "") for p in rel.parts):
        raise ValueError(f"Unsafe document path: {relative}")
    if any(x.lower() in (".git", "secrets", ".ssh", "credentials", "runners.json", "id_rsa")
           or x.lower().startswith(".env") or x.lower().endswith((".pem", ".key", ".p12", ".pfx"))
           for x in rel.parts):
        raise ValueError(f"Restricted context path: {relative}")
    path = (base / rel).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError(f"Context or evidence file unavailable: {relative}")
    if path.stat().st_size > MAX_DOC_BYTES:
        raise ValueError(f"Context/evidence file too large: {relative}")
    return path


def build_prompt(project, task):
    root = Path(project).resolve()
    mandatory = ["AGENTS.md",f".uasef/roles/{task['role']}.md", f".agents/skills/{task['skill']}/SKILL.md"]
    candidates = mandatory + task["context_paths"]
    seen = set()
    docs = []
    total = 0
    for rel in candidates:
        if rel in seen:
            continue
        seen.add(rel)
        file = safe_document(root,rel)
        blob = file.read_text(encoding="utf-8")
        total += len(blob.encode("utf-8"))
        if total > MAX_CONTEXT_BYTES:
            raise ValueError("Context limit exceeded; reduce referenced documents")
        docs.append(f"\n### {rel}\n\n{blob}\n")
    return (f"# UASEF Scoped Task {task['id']}\n\n"
            f"Role: {task['role']}\nSkill: {task['skill']}\n"
            f"Title: {task['title']}\n\nAcceptance criteria:\n{task['acceptance']}\n\n"
            "Follow the project rules. Read the repository and verify the actual state. "
            "Prefer vetted existing solutions to custom code. Stay within task scope. "
            "Never approve your own work, claim tests ran without evidence, "
            "access production without authorization, or commit secrets. "
            "Document changes, tests run, failures, and remaining work. "
            "A successful process exit is NOT verified task completion.\n\n"
            "# Authoritative context\n" + "\n".join(docs))


def load_runner_config(project):
    path = Path(project).resolve() / ".uasef" / "runners.json"
    result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"profiles":{"manual":{"type":"manual"}}}
    if not isinstance(result,dict) or not isinstance(result.get("profiles"),dict):
        raise ValueError("Invalid runners.json: expected profiles object")
    return result


def load_profiles(project):
    return load_runner_config(project)["profiles"]


def prepare(project, task, run_id="preview"):
    base = Path(project).resolve() / ".uasef" / "runs" / run_id
    base.mkdir(parents=True, exist_ok=True)
    prompt = base / "prompt.md"
    prompt.write_text(build_prompt(project,task), encoding="utf-8")
    return prompt


def make_worktree(project, task_id, run_id):
    project = Path(project).resolve()
    check = subprocess.run(["git","-C",str(project),"rev-parse","--show-toplevel"],capture_output=True,text=True,check=False)
    if check.returncode or Path(check.stdout.strip()).resolve() != project:
        raise ValueError("--worktree requires the project root to be a Git repository")
    location = project / ".uasef" / "worktrees" / task_id.lower() / run_id
    branch = f"uasef/{task_id.lower()}/{run_id[:10]}"
    location.parent.mkdir(parents=True,exist_ok=True)
    command = ["git","-C",str(project),"worktree","add","-b",branch,str(location),"HEAD"]
    with _WORKTREE_LOCK:
        result = subprocess.run(command, capture_output=True,text=True,check=False)
    if result.returncode:
        raise ValueError(f"Unable to create isolated worktree: {result.stderr[-600:]}")
    return location


def validate_profile(profile):
    if profile.get("type") != "subprocess":
        raise ValueError("Only opt-in subprocess profiles can execute")
    argv = profile.get("argv")
    if not isinstance(argv,list) or not argv or not all(isinstance(x,str) and x and "\x00" not in x for x in argv):
        raise ValueError("Runner argv must be a nonempty array of safe string arguments")
    timeout = profile.get("timeout_seconds",600)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise ValueError("timeout_seconds must be an integer from 1 to 3600")
    return timeout


def execute(project, profile_name, profile, prompt_path, log_path, cwd, task_id):
    timeout = validate_profile(profile)
    argv = profile["argv"]
    env = dict(os.environ)
    env.update({"UASEF_TASK_ID":task_id,"UASEF_PROMPT_FILE":str(prompt_path),"UASEF_RUN_PROFILE":profile_name})
    # No shell=True, but the configured program still executes with user permissions.
    prompt = prompt_path.read_bytes()
    with open(log_path,"wb") as output:
        try:
            completed = subprocess.run(argv, input=prompt, stdout=output, stderr=subprocess.STDOUT,
                                       cwd=cwd, env=env, timeout=timeout, check=False)
            return completed.returncode, ""
        except subprocess.TimeoutExpired:
            return 124, "Runner timeout; inspect process tree and worktree before retry"
        except OSError as e:
            return 127, f"Runner could not launch: {type(e).__name__}: {e}"

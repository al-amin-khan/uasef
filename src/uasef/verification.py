"""Explicit command execution with commit-bound, locally asserted receipts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid

from . import memory


def revision(project):
    root = Path(project).resolve()
    top = memory.git(root, "rev-parse", "--show-toplevel", required=True)
    if Path(top).resolve() != root:
        raise ValueError("Verification requires the Git repository root")
    head = memory.git(root, "rev-parse", "HEAD", required=True)
    dirty = memory.git(root, "status", "--porcelain", "--untracked-files=all", "--", ".",
                       ":(exclude).uasef/verification/**", required=True)
    if dirty:
        raise ValueError("Commit or remove working-tree changes before verification")
    return head


def folder(project):
    root = Path(project).resolve()
    path = root / ".uasef/verification"
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("Unsafe verification directory")
    return path


def execute(project, argv, timeout=300):
    if not argv or not 1 <= timeout <= 3600:
        raise ValueError("Provide a command and timeout between 1 and 3600 seconds")
    head = revision(project)
    started = memory.stamp()
    # Capture no stdout/stderr in receipts: test logs can contain credentials.
    # The command remains explicitly user-authorized and runs with user privileges.
    try:
        result = subprocess.run(argv, cwd=project, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
        code = result.returncode
    except subprocess.TimeoutExpired:
        code = 124
    except OSError:
        code = 127
    try:
        unchanged = revision(project) == head
    except ValueError:
        unchanged = False
    identifier = "VER-" + uuid.uuid4().hex
    row = {"schema_version": 1, "id": identifier, "commit": head, "argv": argv,
           "started_at": started, "finished_at": memory.stamp(), "exit_code": code,
           "unchanged": unchanged, "passed": code == 0 and unchanged}
    target = folder(project)
    target.mkdir(parents=True, exist_ok=True)
    with (target / (identifier + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(row, stream, indent=2)
    return row


def require_current(project, identifier):
    if not re.fullmatch(r"VER-[a-f0-9]{32}", identifier):
        raise ValueError("Invalid verification ID")
    path = folder(project) / (identifier + ".json")
    if path.is_symlink():
        raise ValueError("Unsafe verification receipt")
    row = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(row, dict) or row.get("schema_version") != 1 or row.get("id") != identifier
            or row.get("passed") is not True or row.get("unchanged") is not True or row.get("exit_code") != 0
            or row.get("commit") != revision(project)):
        raise ValueError("Verification failed or is stale; rerun against the current clean commit")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(project, identifier=None):
    policy = Path(project) / ".uasef/verification-policy.json"
    if policy.exists():
        value = json.loads(policy.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or not isinstance(value.get("required"), bool):
            raise ValueError("Invalid verification policy: expected required boolean")
        if value["required"] and not identifier:
            raise ValueError("Project policy requires --verification VER-ID")
    return require_current(project, identifier) if identifier else None


def run(args):
    if args.verification_action == "check":
        require_current(args.project, args.id)
        print("Verification matches current clean commit; receipt is a local assertion")
        return 0
    argv = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv
    row = execute(args.project, argv, args.timeout)
    print(json.dumps(row, indent=2))
    return 0 if row["passed"] else 1


def attach(sub):
    import argparse
    q = sub.add_parser("verification", help="Execute explicit checks tied to a clean Git commit")
    actions = q.add_subparsers(dest="verification_action", required=True)
    for name in ("run", "check"):
        p = actions.add_parser(name)
        p.add_argument("--project", default=".")
        p.set_defaults(func=run)
        if name == "run":
            p.add_argument("--timeout", type=int, default=300)
            p.add_argument("argv", nargs=argparse.REMAINDER)
        else:
            p.add_argument("id")

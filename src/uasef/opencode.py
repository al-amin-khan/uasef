"""OpenCode CLI adapter: explicit, noninteractive, task-scoped execution.

OpenCode is a third-party CLI. Its permissions, authentication and models must be
configured by the operator. This adapter never silently approves actions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

# Keep platform startup/config variables; provider credentials require explicit opt-in.
_OS_ENV = frozenset({
    "PATH", "HOME", "USER", "USERNAME", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME",
    "TMP", "TEMP", "TMPDIR", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
    "LANG", "LC_ALL", "TERM", "SSL_CERT_FILE", "SSL_CERT_DIR", "NODE_EXTRA_CA_CERTS",
})


def ensure_installed(profile):
    """Reject missing executables before the orchestrator claims a task."""
    binary = profile["argv"][0]
    if not shutil.which(binary):
        raise ValueError(f"OpenCode runner executable not found: {binary}. Install OpenCode and verify PATH.")


def _environment(profile, task_id, profile_name, prompt_file):
    wanted = _OS_ENV | set(profile.get("env_allowlist", []))
    # Windows environment variable names are case-insensitive.
    upper_wanted = {x.upper() for x in wanted}
    env = {k: v for k, v in os.environ.items() if k.upper() in upper_wanted}
    env.update({"UASEF_TASK_ID": task_id, "UASEF_RUN_PROFILE": profile_name,
                "UASEF_PROMPT_FILE": str(prompt_file)})
    return env


def _inspect_events(log_path, summary_path):
    """Inspect NDJSON for explicit errors; never claim task correctness from events."""
    events = 0
    errors = []
    session_ids = set()
    with Path(log_path).open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                # The CLI can emit non-JSON diagnostics; retain them in the log.
                continue
            if not isinstance(item, dict) or not isinstance(item.get("type"), str):
                continue
            events += 1
            part = item.get("part")
            if (item["type"] == "error" or
                (isinstance(part, dict) and
                 (part.get("type") == "error" or part.get("error") or part.get("reason") == "error"))):
                errors.append(str(item.get("error") or part or item)[:500])
            for key in ("sessionID", "sessionId", "session_id"):
                if isinstance(item.get(key), str):
                    session_ids.add(item[key])
    summary = {"format": "opencode-ndjson", "events": events,
               "errors": errors[:20], "session_ids": sorted(session_ids),
               "verified": False}
    Path(summary_path).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def execute_opencode(profile_name, profile, prompt_path, log_path, cwd, task_id, timeout):
    """Use --file instead of stdin/huge argv; OpenCode run accepts file attachments.

    The attachment is placed in the active worktree, not the parent project's
    ignored run directory, so the CLI can access it as a project-local file.
    """
    workspace = Path(cwd).resolve()
    source = Path(prompt_path).resolve()
    # Only attach the already scoped prompt; never allow arbitrary external files.
    relative = Path(".uasef") / "runs" / source.parent.name / "opencode-task.md"
    attachment = workspace / relative
    attachment.parent.mkdir(parents=True, exist_ok=True)
    # Avoid accidental commits of generated prompts in fresh worktrees.
    ignored = workspace / ".uasef" / ".gitignore"
    if not ignored.exists():
        ignored.write_text("runs/\nworktrees/\nsessions/\n", encoding="utf-8")
    shutil.copyfile(source, attachment)
    command = list(profile["argv"]) + ["run", "--format", "json",
               "--agent", profile.get("agent", "build")]
    if profile.get("model"):
        command.extend(["--model", profile["model"]])
    command.extend(["--file", str(attachment),
                    "Follow the attached UASEF task instructions. Read all acceptance criteria, "
                    "work only within the authorized project scope, and report tests and changes. "
                    "Do not self-approve the task."])
    env = _environment(profile, task_id, profile_name, attachment)
    stderr_path = Path(log_path).with_name("runner.stderr.log")
    summary_path = Path(log_path).with_name("opencode-summary.json")
    try:
        with Path(log_path).open("wb") as stdout, stderr_path.open("wb") as stderr:
            completed = subprocess.run(command, stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, cwd=workspace, env=env,
                timeout=timeout, check=False)
        summary = _inspect_events(log_path, summary_path)
        if completed.returncode:
            return completed.returncode, f"OpenCode exited {completed.returncode}; inspect runner logs"
        if summary["errors"]:
            return 1, "OpenCode emitted error events; inspect opencode-summary.json"
        if summary["events"] == 0:
            return 1, "OpenCode returned no JSON events; check CLI version and logs"
        return 0, ""
    except subprocess.TimeoutExpired:
        return 124, "OpenCode timeout; check for orphan child processes before retry"
    except OSError as e:
        return 127, f"OpenCode could not launch: {type(e).__name__}: {e}"

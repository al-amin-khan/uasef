"""Local diagnostics with explicit opt-in external agent probes; never installs hooks."""
import json
from pathlib import Path
import shutil
import sys
import os
import re
import subprocess
import tempfile


def command(argv, cwd, timeout=15, env=None):
    """Never expose subprocess diagnostics, which can contain credentials."""
    try:
        result = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                capture_output=True, encoding="utf-8", errors="replace",
                                timeout=timeout, env=env)
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 124, ""
    except OSError:
        return 127, ""


def hooks(project, add):
    code, root = command(["git", "-C", str(project), "rev-parse", "--show-toplevel"], project)
    if code:
        add("hooks.activation", "warning", "Git repository unavailable", "Initialize Git or select its working tree.")
        return
    root = Path(root.strip())
    code, location = command(["git", "-C", str(root), "rev-parse", "--git-path", "hooks"], root)
    if code or not location.strip():
        add("hooks.activation", "warning", "Cannot resolve effective hook directory")
        return
    directory = Path(location.strip())
    if not directory.is_absolute():
        directory = root / directory
    for name in ("pre-commit", "commit-msg"):
        path = directory / name
        try:
            if not path.is_file():
                detail = "Missing effective hook"
            elif os.name != "nt" and not os.access(path, os.X_OK):
                detail = "Hook is not executable"
            else:
                text = path.read_text(encoding="utf-8", errors="replace")
                detail = "Lefthook launcher detected; not executed" if "lefthook" in text.lower() else "Custom hook detected; behavior unknown"
            add("hooks." + name, "warning", detail,
                "Review effective hooks and configuration. Static inspection cannot prove enforcement.")
        except OSError:
            add("hooks." + name, "error", "Hook could not be read")
    if any(os.environ.get(k) for k in ("LEFTHOOK", "LEFTHOOK_EXCLUDE", "LEFTHOOK_SKIP", "SKIP")):
        add("hooks.environment", "warning", "Hook control environment variables are set; review possible bypasses")


def agent_checks(add, auth=False, live=False, model=None, timeout=60):
    if not (auth or live):
        add("agent.authentication", "skipped", "Use --auth to inspect OpenCode provider configuration")
        add("agent.connectivity", "skipped", "Use --live --model provider/model for a billable model probe")
        return
    binary = shutil.which("opencode")
    if not binary:
        add("agent", "error", "OpenCode not found on PATH")
        return
    # No project files or prompts are attached. External CLI global configuration
    # still applies: a temporary working directory is not a security sandbox.
    with tempfile.TemporaryDirectory(prefix="uasef-doctor-") as directory:
        if auth:
            code, output = command([binary, "auth", "list", "--format", "json"], directory, timeout)
            if code:
                add("agent.authentication", "error", f"OpenCode auth command failed (exit {code}); credentials not assessed",
                    "Run opencode auth list in your terminal to inspect the startup/authentication error.")
            else:
                try:
                    data = json.loads(output)
                    populated = isinstance(data, (list, dict)) and bool(data)
                    add("agent.authentication", "warning", "Provider configuration returned; validity unverified" if populated else "No provider configuration confirmed",
                        "Use the live probe to verify access to a selected model.")
                except ValueError:
                    add("agent.authentication", "warning", "Auth output format unsupported; credentials not assessed")
        if live:
            env = dict(os.environ)
            env.update(OPENCODE_PERMISSION='{"*":"deny"}', OPENCODE_DISABLE_AUTOUPDATE="true",
                       OPENCODE_DISABLE_PROJECT_CONFIG="true", OPENCODE_DISABLE_DEFAULT_PLUGINS="true",
                       OPENCODE_PURE="true")
            code, output = command([binary, "run", "--format", "json", "--model", model,
                                    "Reply with exactly UASEF_DOCTOR_OK. Do not use tools."], directory, timeout, env)
            acknowledged = False
            failed = bool(code)
            for line in output.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                part = event.get("part")
                failed |= event.get("type") == "error"
                if isinstance(part, dict):
                    failed |= bool(part.get("error")) or part.get("type") == "error"
                    acknowledged |= event.get("type") == "text" and isinstance(part.get("text"), str) and part["text"].strip() == "UASEF_DOCTOR_OK"
            add("agent.connectivity", "ok" if acknowledged and not failed else "error",
                "Selected model answered the probe; access verified for this request only" if acknowledged and not failed
                else f"No verified model response (exit {code}); startup, auth, quota or network may be responsible",
                "Check the selected model and provider configuration. Timeout may leave child processes; inspect before retrying.")


def diagnose(project, auth=False, live=False, model=None, timeout=60):
    if not 1 <= timeout <= 300:
        raise ValueError("Timeout must be between 1 and 300 seconds")
    if live and (not model or not re.fullmatch(r"[A-Za-z0-9_.:-]+/[A-Za-z0-9_./:#-]+", model)):
        raise ValueError("Live probe requires --model provider/model")
    from .cli import framework_root
    checks = []

    def add(name, status, detail, fix=""):
        checks.append(dict(name=name, status=status, detail=detail, fix=fix))

    add("python", "ok" if sys.version_info >= (3, 10) else "error", sys.version.split()[0],
        "Use Python 3.10 or newer.")
    try:
        root = framework_root()
        missing = [name for name in ("workflows", "templates", "policies", "agents", "skills", "schemas") if not (root / name).is_dir()]
        add("resources", "error" if missing else "ok", "Missing: " + ", ".join(missing) if missing else str(root),
            "Reinstall a complete UASEF wheel or editable source checkout.")
    except RuntimeError as exc:
        add("resources", "error", str(exc), "Reinstall a complete UASEF wheel or editable source checkout.")
    for name in ("git", "lefthook", "cog", "opencode", "codex", "claude"):
        found = shutil.which(name)
        add(name, "ok" if found else "warning", found or "Not found on PATH",
            "Install or add to PATH if needed. Agent and hook tools are optional.")
    project = Path(project).resolve()
    if not project.is_dir():
        add("project", "error", "Project directory does not exist", "Select an existing directory with --project.")
    else:
        state = project / ".uasef" / "state.json"
        if not state.exists():
            add("project", "warning", "No UASEF inception state", "Initialize this project with uasef init <path> --existing.")
        else:
            try:
                data = json.loads(state.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
                    raise ValueError("Expected state object with tasks list")
                add("project", "ok", "Inception state readable (basic structure only)")
            except (OSError, ValueError) as exc:
                add("project", "error", str(exc), "Restore state from a known-good backup; do not reinitialize over it.")
        memory = project / "docs" / "project-memory"
        if memory.exists():
            try:
                from .memory import records
                rows = records(project)
                add("memory", "ok", f"{len(rows)} records readable; evidence authenticity not verified")
            except (OSError, ValueError, RuntimeError) as exc:
                add("memory", "error", str(exc), "Review the reported memory record and restore or repair it.")
        else:
            add("memory", "warning", "No project memory", "Run uasef upgrade for an initialized project.")
        add("hooks", "ok" if (project / "lefthook.yml").is_file() else "warning",
            "Configuration present; activation not verified" if (project / "lefthook.yml").is_file() else "No lefthook.yml",
            "Use uasef upgrade --git-hooks, review existing hooks, then lefthook install.")
        hooks(project, add)
    agent_checks(add, auth, live, model, timeout)
    return {"schema_version": 1, "checks": checks, "healthy": not any(c["status"] == "error" for c in checks)}


def run(args):
    report = diagnose(args.project, args.auth, args.live, args.model, args.timeout)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for check in report["checks"]:
            print(f"[{check['status'].upper()}] {check['name']}: {check['detail']}")
            if check["status"] != "ok" and check["fix"]:
                print(f"  Fix: {check['fix']}")
    return 0 if report["healthy"] else 1

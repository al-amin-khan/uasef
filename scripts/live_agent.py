"""Opt-in provider-backed adapter test. Uses the operator's configured OpenCode."""
import argparse
import json
from pathlib import Path
import tempfile

from uasef.opencode import ensure_installed, execute_opencode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Explicit configured provider/model; may incur charges")
    parser.add_argument("--execute", action="store_true", help="Invoke the real agent with existing global permissions")
    parser.add_argument("--env", action="append", default=[], help="Provider environment variable NAME to pass; never its value")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if not args.execute:
        parser.error("Pass --execute to run the provider-backed test")
    if not 1 <= args.timeout <= 600:
        parser.error("Timeout must be between 1 and 600 seconds")
    profile = {"type": "opencode", "argv": ["opencode"], "model": args.model, "agent": "build", "env_allowlist": args.env}
    ensure_installed(profile)
    # Global agent configuration/permissions apply. This is not an OS sandbox.
    with tempfile.TemporaryDirectory(prefix="uasef-real-agent-") as temporary:
        root = Path(temporary)
        logs = root / "evidence"
        logs.mkdir()
        prompt = logs / "prompt.md"
        prompt.write_text('Create only result.json in the current directory, containing exactly {"answer":42}. Do not use network tools or modify any other project files. This is a disposable UASEF adapter test. Do not claim review or approval.', encoding="utf-8")
        code, error = execute_opencode("live-test", profile, prompt, logs / "runner.log", root, "LIVE-001", args.timeout)
        if code:
            raise SystemExit(f"FAILED: adapter exit {code}; {error}. No provider success claimed.")
        output = root / "result.json"
        if output.is_symlink() or not output.is_file() or output.stat().st_size > 1024 or json.loads(output.read_text()) != {"answer": 42}:
            raise SystemExit("FAILED: expected artifact was not produced")
        print(json.dumps({"passed": True, "model": args.model, "check": "real OpenCode adapter produced independently checked JSON artifact"}))


if __name__ == "__main__":
    main()

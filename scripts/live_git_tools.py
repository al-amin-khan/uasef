"""Real Git/Lefthook/Cocogitto integration. Requires installed binaries on PATH."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run(root, *args, success=True):
    result = subprocess.run(args, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if (result.returncode == 0) != success:
        raise AssertionError(f"Unexpected result for {args}:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def main():
    for command in (("lefthook", "version"), ("cog", "--version")):
        print(run(Path.cwd(), *command), flush=True)
    # Ignore inherited developer bypass switches during this disposable test.
    for name in ("LEFTHOOK", "LEFTHOOK_EXCLUDE", "LEFTHOOK_SKIP", "SKIP"):
        os.environ.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="uasef-live-") as temporary:
        root = Path(temporary) / "project with spaces"
        run(Path.cwd(), sys.executable, "-m", "uasef", "init", str(root), "--git-hooks")
        assert (root / "lefthook.yml").is_file()
        run(root, "git", "init")
        run(root, "git", "config", "user.name", "UASEF Integration")
        run(root, "git", "config", "user.email", "integration@example.invalid")
        run(root, "lefthook", "install")
        file = root / "example.txt"
        file.write_text("initial\n", encoding="utf-8")
        run(root, "git", "add", "example.txt", "lefthook.yml")
        run(root, "git", "commit", "-m", "feat: initial example")
        original = run(root, "git", "rev-parse", "HEAD")
        file.write_text("changed\n", encoding="utf-8")
        run(root, "git", "add", "example.txt")
        run(root, "git", "commit", "-m", "updated stuff", success=False)
        assert run(root, "git", "rev-parse", "HEAD") == original
        run(root, "git", "commit", "-m", "fix: update example")
        file.write_text("trailing space   \n", encoding="utf-8")
        run(root, "git", "add", "example.txt")
        run(root, "git", "commit", "-m", "fix: whitespace example", success=False)
        file.write_text("clean\n", encoding="utf-8")
        run(root, "git", "add", "example.txt")
        before = run(root, "git", "rev-parse", "HEAD")
        run(root, sys.executable, "-m", "uasef", "memory", "checkpoint", "--message", "bad message", success=False)
        assert run(root, "git", "rev-parse", "HEAD") == before
        run(root, sys.executable, "-m", "uasef", "memory", "checkpoint", "--message", "docs(memory): preserve initial history")
        assert run(root, "git", "diff", "--cached", "--name-only") == "example.txt"
        assert all(p.startswith("docs/project-memory/") for p in run(root, "git", "show", "--pretty=", "--name-only", "HEAD").splitlines())
        run(root, "cog", "check")
        config = root / "lefthook.yml"
        config.write_text("# owner customization\n", encoding="utf-8")
        run(root, sys.executable, "-m", "uasef", "upgrade", "--git-hooks")
        assert config.read_text() == "# owner customization\n"
        print("PASS: valid/invalid commits, whitespace, memory hooks, staging isolation, history and upgrade preservation", flush=True)


if __name__ == "__main__":
    main()

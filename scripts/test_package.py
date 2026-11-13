"""Build sdist -> wheel, install into a clean venv and exercise packaged resources."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(argv, cwd, env):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                            capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"Command failed: {argv}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def main():
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    with tempfile.TemporaryDirectory(prefix="uasef-package-") as temporary:
        base = Path(temporary)
        dist = base / "dist"
        # build's default flow creates an sdist, then builds its wheel from that sdist.
        run([sys.executable, "-m", "build", "--outdir", dist, ROOT], base, env)
        wheel, = dist.glob("*.whl")
        with zipfile.ZipFile(wheel) as archive:
            for directory in ("agents", "skills", "policies", "templates", "workflows", "schemas"):
                for source in (ROOT / directory).rglob("*"):
                    if source.is_file() and source.suffix in (".md", ".json", ".yaml", ".yml"):
                        name = "uasef/_resources/" + source.relative_to(ROOT).as_posix()
                        assert archive.read(name) == source.read_bytes(), name
            for name in ("framework.json", "lefthook.yml"):
                assert archive.read("uasef/_resources/" + name) == (ROOT / name).read_bytes()
        environment = base / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        binaries = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        cli = binaries / ("uasef.exe" if os.name == "nt" else "uasef")
        run([python, "-m", "pip", "install", "--no-index", "--no-deps", wheel], base, env)
        resource_root = Path(run([python, "-I", "-c", "from uasef.cli import framework_root; print(framework_root())"], base, env).strip())
        assert resource_root.resolve().is_relative_to(environment.resolve()), resource_root
        assert resource_root.name == "_resources"
        project = base / "project with spaces"
        run([cli, "init", project, "--git-hooks", "--idea", "Verify standalone packaging"], base, env)
        assert list((project / ".agents" / "skills").glob("*/SKILL.md"))
        assert list((project / ".uasef" / "roles").glob("*.md"))
        assert (project / "lefthook.yml").is_file()
        charter = project / "AGENTS.md"
        charter.write_text("Owner customization\n", encoding="utf-8")
        run([cli, "upgrade", "--git-hooks"], project, env)
        assert charter.read_text() == "Owner customization\n"
        report = json.loads(run([cli, "doctor", "--json"], project, env))
        assert report["healthy"], report
        assert "Verify standalone packaging" in run([cli, "memory", "brief"], project, env)
        run([cli, "memory", "validate"], project, env)
        run([cli, "memory", "timeline"], project, env)
        run([cli, "memory", "conflicts"], project, env)
        run([cli, "memory", "search", "standalone"], project, env)
        archive = base / "state.zip"
        run([cli, "backup", archive], project, env)
        restored = base / "restored"
        run([cli, "restore", archive, restored], base, env)
        run([cli, "upgrade"], restored, env)
        assert "Verify standalone packaging" in run([cli, "memory", "brief"], restored, env)
        run([python, "-I", "-m", "uasef", "--help"], base, env)
        print("PASS: sdist-built wheel, exact resource bytes, isolated install, init, upgrade, doctor and memory")


if __name__ == "__main__":
    main()

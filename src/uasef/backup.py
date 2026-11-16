"""Versioned UASEF state backups, not source-code or credential backups."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import tempfile
import zipfile

from . import memory

MAX_BYTES = 100 * 1024 * 1024
MAX_FILES = 20000
DB = ".uasef/orchestration.sqlite3"


def allowed(name):
    p = PurePosixPath(name)
    if (not name or "\\" in name or ":" in name or p.is_absolute()
            or any(x in ("", ".", "..") for x in name.split("/"))):
        return False
    if name in (".uasef/state.json", DB):
        return True
    return (name.startswith("docs/project-memory/") and
            (name in ("docs/project-memory/project.json", "docs/project-memory/README.md") or
             (p.parent.as_posix() == "docs/project-memory/records" and
              p.suffix == ".json" and memory.ID_RE.fullmatch(p.stem))))


def validate_state(root):
    from .cli import load
    state = load(root)
    if (not isinstance(state, dict) or state.get("schema_version") != 1 or
            state.get("framework_version") not in ("0.1.0", "0.2.0", "0.3.0", "0.4.0", "0.5.0", "0.6.0", "0.7.0") or
            not isinstance(state.get("tasks"), list) or not isinstance(state.get("idea"), str)):
        raise ValueError("Unsupported or malformed inception state")
    for task in state["tasks"]:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise ValueError("Malformed inception task")
    if (memory.directory(root) / "project.json").exists():
        memory._json(memory.directory(root) / "project.json")
        memory.records(root)


def database(root, reset=False):
    path = Path(root) / DB
    if not path.exists():
        return
    with closing(sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)) as conn:
        conn.execute("PRAGMA trusted_schema=OFF")
        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Database integrity check failed")
        if conn.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Database foreign-key check failed")
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"tasks", "runs", "audit"} <= tables:
            raise ValueError("Unsupported orchestration database")
        if conn.execute("SELECT count(*) FROM sqlite_master WHERE type IN ('trigger','view')").fetchone()[0]:
            raise ValueError("Unexpected database triggers or views")
        running = conn.execute("SELECT id FROM tasks WHERE status='running'").fetchall()
        if running and not reset:
            raise ValueError("Stop workers and recover running tasks before backing up")
        if reset:
            conn.execute("UPDATE tasks SET status='failed' WHERE status='running'")
            conn.execute("UPDATE tasks SET lease_token=NULL,lease_until=NULL")
            conn.execute("UPDATE runs SET status='interrupted',error='Restored backup; inspect worker before retry' WHERE status='running'")
            conn.commit()


def create(project, destination):
    root = Path(project).resolve()
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError("Backup must be a new file outside the project")
    validate_state(root)
    selected = [root / ".uasef/state.json"]
    selected += [p for p in memory.directory(root).rglob("*") if p.is_file()]
    if len(selected) > MAX_FILES or sum(p.stat().st_size for p in selected) > MAX_BYTES:
        raise ValueError("Backup exceeds supported size")
    blobs = {}
    for path in selected:
        relative = path.relative_to(root).as_posix()
        if not allowed(relative) or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Unexpected or unsafe backup file: " + relative)
        blobs[relative] = path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="uasef-snapshot-") as folder:
        snapshot = Path(folder)
        if (root / DB).exists():
            if (root / DB).stat().st_size > MAX_BYTES:
                raise ValueError("Database exceeds supported backup size")
            if (root / DB).is_symlink() or not (root / DB).resolve().is_relative_to(root):
                raise ValueError("Unsafe database path")
            (snapshot / DB).parent.mkdir(parents=True)
            with closing(sqlite3.connect((root / DB).as_uri() + "?mode=ro", uri=True)) as source, closing(sqlite3.connect(snapshot / DB)) as target:
                source.backup(target)
            database(snapshot)
            blobs[DB] = (snapshot / DB).read_bytes()
        # Detect concurrent file edits instead of claiming a consistent multi-file snapshot.
        if any(path.read_bytes() != blobs[path.relative_to(root).as_posix()] for path in selected):
            raise ValueError("Project changed during backup; stop writers and retry")
        if len(blobs) > MAX_FILES or sum(map(len, blobs.values())) > MAX_BYTES:
            raise ValueError("Backup exceeds supported size")
        manifest = {"schema_version": 1, "scope": "uasef-state", "at": memory.stamp(),
                    "files": {n: hashlib.sha256(b).hexdigest() for n, b in blobs.items()}}
        # Exclusive creation prevents replacing an existing backup.
        with destination.open("xb") as output:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("manifest.json", json.dumps(manifest))
                for name, blob in blobs.items():
                    archive.writestr(name, blob)
    return str(destination)


def restore(archive_path, destination):
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Restore requires a new, nonexistent destination directory")
    if not destination.parent.is_dir():
        raise ValueError("Restore parent directory must already exist")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            names = [i.filename for i in infos]
            if (len(names) > MAX_FILES + 1 or len(set(n.casefold() for n in names)) != len(names)
                    or sum(i.file_size for i in infos) > MAX_BYTES):
                raise ValueError("Oversized or duplicate backup entries")
            if "manifest.json" not in names or any(n != "manifest.json" and not allowed(n) for n in names):
                raise ValueError("Unexpected backup entries")
            manifest = json.loads(archive.read("manifest.json"))
            if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or manifest.get("scope") != "uasef-state" or not isinstance(manifest.get("files"), dict):
                raise ValueError("Unsupported backup format")
            if set(names) != set(manifest["files"]) | {"manifest.json"} or ".uasef/state.json" not in names:
                raise ValueError("Backup manifest does not match archive")
            with tempfile.TemporaryDirectory(prefix=".uasef-restore-", dir=destination.parent) as folder:
                staging = Path(folder) / "project"
                staging.mkdir()
                for name, expected in manifest["files"].items():
                    data = archive.read(name)
                    if hashlib.sha256(data).hexdigest() != expected:
                        raise ValueError("Backup checksum mismatch: " + name)
                    path = staging / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                validate_state(staging)
                database(staging, reset=True)
                # No imported runner configuration is executed or installed.
                os.rename(staging, destination)
    except (zipfile.BadZipFile, sqlite3.DatabaseError) as exc:
        raise ValueError("Invalid backup archive/database") from exc
    return str(destination)


def attach(sub):
    q = sub.add_parser("backup", help="Back up UASEF state only; stop writers first")
    q.add_argument("destination")
    q.add_argument("--project", default=".")
    q.set_defaults(func=lambda a: print(create(a.project, a.destination)))
    q = sub.add_parser("restore", help="Restore state into a new directory; source code remains in Git")
    q.add_argument("archive")
    q.add_argument("destination")
    q.set_defaults(func=lambda a: print(restore(a.archive, a.destination)))

"""OS-released ownership locks for local workers, not persistent PID guesses."""
from contextlib import contextmanager
import os
from pathlib import Path


@contextmanager
def own(project, task_id):
    path = Path(project).resolve() / ".uasef" / "runs" / ".worker-locks" / (task_id + ".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("A managed worker still owns this task; cancel it and wait before retry") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def active(project, task_id):
    try:
        with own(project, task_id):
            return False
    except ValueError:
        return True

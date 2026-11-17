"""Bounded local subprocess execution with owned process-tree cleanup."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

# A Windows wrapper cannot start the configured program until its job is assigned.
_WINDOWS_WRAPPER = """import json,subprocess,sys
if sys.stdin.buffer.read(1) != b'G':
    sys.exit(127)
source = open(sys.argv[2], 'rb') if sys.argv[2] else subprocess.DEVNULL
try:
    child = subprocess.Popen(json.loads(sys.argv[1]), stdin=source)
    sys.exit(child.wait())
except OSError:
    sys.exit(127)
"""


def run(argv, cwd, env, timeout, log_path, *, stdin_path=None, stderr_path=None,
        cancel_check=None, max_output_bytes=1048576):
    started = time.monotonic()
    process = None
    job = None
    source = None
    threads = []
    exceeded = threading.Event()
    io_error = threading.Event()
    budget_lock = threading.Lock()
    remaining = max_output_bytes
    code, error = 127, "Runner did not start"

    def drain(pipe, target):
        nonlocal remaining
        try:
            with Path(target).open("wb") as output:
                while True:
                    data = pipe.read1(8192)
                    if not data:
                        break
                    with budget_lock:
                        kept = data[:remaining]
                        remaining -= len(kept)
                        if len(kept) != len(data):
                            exceeded.set()
                    output.write(kept)
        except OSError:
            io_error.set()
        finally:
            pipe.close()

    def stop():
        if process is None:
            return
        if job is not None:
            job.stop()
        elif os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        process.wait(timeout=10)

    try:
        if cancel_check and cancel_check():
            return 130, "Cancellation requested before runner launch"
        options = dict(cwd=cwd, env=env, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE if stderr_path else subprocess.STDOUT)
        if os.name == "nt":
            from .windows_job import Job
            job = Job()
            command = [sys.executable, "-I", "-c", _WINDOWS_WRAPPER, json.dumps(argv),
                       str(Path(stdin_path).resolve()) if stdin_path else ""]
            process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW, **options)
            try:
                job.assign(process)
            except OSError:
                process.kill()
                process.wait(timeout=10)
                raise
            process.stdin.write(b"G")
            process.stdin.close()
        else:
            source = open(stdin_path, "rb") if stdin_path else None
            process = subprocess.Popen(argv, stdin=source or subprocess.DEVNULL,
                                       start_new_session=True, **options)
        for pipe, target in ((process.stdout, log_path), (process.stderr, stderr_path)):
            if pipe is not None:
                thread = threading.Thread(target=drain, args=(pipe, target), daemon=True)
                thread.start()
                threads.append(thread)
        while True:
            if cancel_check and cancel_check():
                code, error = 130, "Cancellation requested; managed process tree stopped"
                break
            if exceeded.is_set() or io_error.is_set():
                code, error = 125, "Runner output limit exceeded or log write failed"
                break
            if time.monotonic() - started >= timeout:
                code, error = 124, "Runner timeout; managed process tree stopped"
                break
            result = process.poll()
            if result is not None:
                code, error = result, ""
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        code, error = 130, "Cancellation by keyboard interrupt; managed process tree stopped"
    except OSError as exc:
        code, error = 127, f"Runner could not launch: {type(exc).__name__}: {exc}"
    finally:
        try:
            stop()  # Clean up children even when the top-level command exits normally.
        except (OSError, subprocess.TimeoutExpired) as exc:
            code, error = 125, f"Cleanup uncertain; inspect external processes before retry: {exc}"
        finally:
            if job is not None:
                job.close()
            if source is not None:
                source.close()
        if process is not None and not threads:
            for pipe in (process.stdin, process.stdout, process.stderr):
                if pipe is not None:
                    pipe.close()
        for thread in threads:
            thread.join(timeout=2)
        if any(thread.is_alive() for thread in threads):
            code, error = 125, "Cleanup uncertain; output pipe is still held by an external process"
        elif (exceeded.is_set() or io_error.is_set()) and not error.startswith("Cleanup uncertain"):
            code, error = 125, "Runner output limit exceeded or log write failed"
    return code, error

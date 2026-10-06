from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from .artifacts import runs_root_for
from .catalog import load_catalog, resolve_root
from .contract import DEFAULT_TIMEOUT, validate_timeout
from .receipt import SCHEMA, sha256_bytes, sha256_file, write_receipt

try:
    import fcntl
except ImportError:
    fcntl = None

_process_lock = threading.Lock()

def resolve_bootloops_root(root: str | None = None) -> Path:
    return resolve_root(root or os.environ.get("BOOTLOOPS_ROOT") or "vendor/bootloops")

def _kill_process_group(proc) -> None:
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
            return
        except (ProcessLookupError, PermissionError):
            pass
    try:
        proc.kill()
    except ProcessLookupError:
        pass

class _RunLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None
    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+")
        _process_lock.acquire()
        if fcntl is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self
    def __exit__(self, *_args):
        try:
            if fcntl is not None:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            _process_lock.release()

def run_acceptance(package: str, *, root: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    timeout = validate_timeout(timeout)
    bl = resolve_bootloops_root(root)
    catalog = load_catalog(bl)
    if package not in catalog:
        raise KeyError(f"Package not in canonical BootLoops catalog: {package}")

    job_id = uuid.uuid4().hex
    job_dir = runs_root_for(bl) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    results_path = bl / "selftest_results.json"
    try:
        results_path.unlink()
    except FileNotFoundError:
        pass

    cmd = [sys.executable, str(bl / "run_selftests.py"), package, "--timeout", str(timeout)]
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).resolve().parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = os.pathsep.join([
        str(bl / "tools"),
        str(bl / "tools" / package),
        str(bl),
        env.get("PYTHONPATH", ""),
    ])

    started = time.time()
    stdout = ""
    returncode = -1

    try:
        with _RunLock(Path(os.environ.get(
            "BOOTLOOPS_LAB_RUN_LOCK",
            str(bl.parent / "bootloops-lab" / "run.lock"),
        ))):
            proc = subprocess.Popen(
                cmd,
                cwd=bl,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=(os.name == "posix"),
            )
            try:
                stdout, _ = proc.communicate(timeout=timeout + 60)
                returncode = proc.returncode
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or ""
                _kill_process_group(proc)
                try:
                    tail, _ = proc.communicate(timeout=15)
                    stdout += tail or ""
                except Exception:
                    pass
                returncode = -9
                stdout += f"\nPROCESS TIMEOUT after outer guard ({timeout + 60}s)"
            finally:
                if proc.poll() is None:
                    _kill_process_group(proc)
    except (OSError, subprocess.SubprocessError) as exc:
        stdout += f"\nPROCESS ERROR: {exc}"
        returncode = -8

    (job_dir / "stdout.log").write_text(stdout, encoding="utf-8")

    result_record = None
    result_sha = None
    if results_path.is_file():
        raw = results_path.read_bytes()
        result_sha = sha256_file(results_path)
        (job_dir / "selftest_results.json").write_bytes(raw)
        try:
            result_record = json.loads(raw).get(package)
        except json.JSONDecodeError:
            result_record = None

    if isinstance(result_record, dict):
        status = result_record.get("status", "UNKNOWN")
    elif returncode == -9:
        status = "PROCESS_TIMEOUT"
    elif returncode < 0:
        status = "PROCESS_ERROR"
    else:
        status = "UNKNOWN"

    record = {
        "schema": SCHEMA,
        "job_id": job_id,
        "package": package,
        "verification_class": catalog[package]["verification_class"],
        "status": status,
        "returncode": returncode,
        "timeout_seconds": timeout,
        "elapsed_seconds": round(time.time() - started, 3),
        "bootloops_root": str(bl),
        "bootloops_ref": os.environ.get("BOOTLOOPS_REF", "unknown"),
        "command": cmd,
        "cwd": str(bl),
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "result_sha256": result_sha,
        "result": result_record,
    }
    write_receipt(job_dir / "receipt.json", record)
    return record

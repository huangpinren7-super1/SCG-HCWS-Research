from __future__ import annotations

import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import yaml

from .artifacts import runs_root_for
from .catalog import load_catalog, resolve_root
from .contract import DEFAULT_TIMEOUT, validate_timeout
from .receipt import SCHEMA, sha256_bytes, sha256_file, write_receipt

try:
    import fcntl
except ImportError:
    fcntl = None

_process_lock = threading.Lock()
REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "gateway" / "registry.yaml"
EXPECTED_GENERATED = {"selftest_results.json"}


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}


def expected_bootloops_ref() -> str:
    ref = str(_registry().get("bootloops_ref", ""))
    if len(ref) != 40:
        raise RuntimeError("registry.yaml does not contain a 40-character BootLoops commit SHA")
    return ref


def _git_status(root: Path) -> list[str]:
    p = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"cannot inspect BootLoops git status: {p.stderr.strip()}")
    return [line for line in p.stdout.splitlines() if line.strip()]


def _unexpected_changes(status_lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in status_lines:
        path = line[3:] if len(line) >= 3 else line
        if path not in EXPECTED_GENERATED:
            out.append(line)
    return out


def bootloops_fingerprint(root: str | Path) -> dict[str, Any]:
    bl = resolve_root(root)
    p = subprocess.run(
        ["git", "-C", str(bl), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"cannot determine BootLoops HEAD: {p.stderr.strip()}")
    actual_ref = p.stdout.strip()
    expected_ref = expected_bootloops_ref()
    status = _git_status(bl)
    return {
        "root": str(bl),
        "actual_ref": actual_ref,
        "expected_ref": expected_ref,
        "ref_matches_registry": actual_ref == expected_ref,
        "worktree_clean": not bool(_unexpected_changes(status)),
        "status": status,
    }


def _version(command: str) -> str | None:
    exe = shutil.which(command)
    if not exe:
        return None
    for args in ([exe, "--version"], [exe, "-version"], [exe, "-v"]):
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        text = (p.stdout or p.stderr).strip()
        if text:
            return text.splitlines()[0][:500]
    return None


def _pip_freeze() -> dict[str, str]:
    try:
        p = subprocess.run(
            [sys.executable, "-m", "pip", "freeze", "--disable-pip-version-check"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    out: dict[str, str] = {}
    for line in p.stdout.splitlines():
        if "==" in line and not line.startswith("#"):
            name, version = line.split("==", 1)
            out[name.lower()] = version
    return dict(sorted(out.items()))


def environment_fingerprint(bl: Path) -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "dependencies": _pip_freeze(),
        "engines": {
            name: _version(name)
            for name in (
                "gp", "gphelp", "msolve", "Singular", "julia", "sage",
                "redg1", "fitrel", "fflowcli", "dumppoints",
            )
        },
        "git": bootloops_fingerprint(bl),
    }


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

    # Clear the only expected generated file before the pre-run cleanliness gate.
    results_path = bl / "selftest_results.json"
    try:
        results_path.unlink()
    except FileNotFoundError:
        pass

    fp_before = bootloops_fingerprint(bl)
    if not fp_before["ref_matches_registry"]:
        raise RuntimeError(
            f"BootLoops ref mismatch: actual={fp_before['actual_ref']} "
            f"registry={fp_before['expected_ref']}"
        )
    if not fp_before["worktree_clean"]:
        raise RuntimeError(
            "BootLoops worktree is dirty before execution: "
            + "; ".join(fp_before["status"])
        )

    job_id = uuid.uuid4().hex
    job_dir = runs_root_for(bl) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

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

    post_status = _git_status(bl)
    unexpected_after = _unexpected_changes(post_status)
    environment = environment_fingerprint(bl)

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
        "bootloops_ref": fp_before["actual_ref"],
        "bootloops_worktree_clean_before": True,
        "bootloops_worktree_clean_after": not bool(unexpected_after),
        "unexpected_worktree_changes": unexpected_after,
        "command": cmd,
        "cwd": str(bl),
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "result_sha256": result_sha,
        "environment": environment,
        "result": result_record,
    }
    write_receipt(job_dir / "receipt.json", record)
    return record

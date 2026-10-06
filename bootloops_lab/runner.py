from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from .catalog import load_catalog, resolve_root
from .receipt import SCHEMA, sha256_bytes, write_receipt

DEFAULT_TIMEOUT = 300
MAX_TIMEOUT = 1200


def resolve_bootloops_root(root: str | None = None) -> Path:
    candidate = root or os.environ.get('BOOTLOOPS_ROOT')
    if candidate:
        return resolve_root(candidate)
    local = Path('vendor/bootloops')
    if local.is_dir():
        return resolve_root(local)
    raise FileNotFoundError('BootLoops root unavailable; set BOOTLOOPS_ROOT or use vendor/bootloops.')


class _RunLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open('w')
        fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *_args):
        if self.handle:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()


def run_acceptance(package: str, *, root: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    if not 1 <= timeout <= MAX_TIMEOUT:
        raise ValueError(f'timeout must be between 1 and {MAX_TIMEOUT} seconds')

    bl = resolve_bootloops_root(root)
    catalog = load_catalog(bl)
    if package not in catalog:
        raise KeyError(f'Package not on canonical BootLoops catalog: {package}')

    job_id = uuid.uuid4().hex
    runs_root = Path(os.environ.get('BOOTLOOPS_LAB_RUNS', str(bl.parent / 'bootloops-lab' / 'runs')))
    job_dir = runs_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(bl / 'run_selftests.py'), package, '--timeout', str(timeout)]
    env = dict(os.environ)
    venv_bin = str(Path(sys.executable).resolve().parent)
    env['PATH'] = venv_bin + os.pathsep + env.get('PATH', '')
    tools = bl / 'tools'
    env['PYTHONPATH'] = os.pathsep.join([str(tools), str(tools / package), str(bl), env.get('PYTHONPATH', '')])

    started = time.time()
    try:
        with _RunLock(Path(os.environ.get('BOOTLOOPS_LAB_RUN_LOCK', str(bl.parent / 'bootloops-lab' / 'run.lock')))):
            proc = subprocess.run(
                cmd, cwd=bl, env=env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                timeout=timeout + 60, check=False,
            )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ''
        return _emit_receipt(package, catalog, bl, job_id, timeout, started, -9, stdout, job_dir, 'PROCESS_TIMEOUT')

    return _emit_receipt(package, catalog, bl, job_id, timeout, started, proc.returncode, proc.stdout or '', job_dir, None)


def _emit_receipt(package, catalog, bl, job_id, timeout, started, returncode, stdout, job_dir, fallback):
    (job_dir / 'stdout.log').write_text(stdout)
    result_record = None
    results_path = bl / 'selftest_results.json'
    if results_path.is_file():
        raw = results_path.read_bytes()
        (job_dir / 'selftest_results.json').write_bytes(raw)
        try:
            all_results = json.loads(raw)
            result_record = all_results.get(package, all_results)
        except json.JSONDecodeError:
            result_record = None
    status = result_record.get('status') if isinstance(result_record, dict) else fallback
    if status is None:
        status = 'PROCESS_ERROR' if returncode else 'UNKNOWN'
    record = {
        'schema': SCHEMA,
        'job_id': job_id,
        'package': package,
        'verification_class': catalog[package]['verification_class'],
        'status': status,
        'returncode': returncode,
        'timeout_seconds': timeout,
        'elapsed_seconds': round(time.time() - started, 3),
        'bootloops_root': str(bl),
        'bootloops_ref': os.environ.get('BOOTLOOPS_REF', 'unknown'),
        'stdout_sha256': sha256_bytes(stdout.encode()),
        'result': result_record,
    }
    write_receipt(job_dir / 'receipt.json', record)
    return record
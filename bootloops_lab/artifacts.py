from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from .receipt import sha256_file

MAX_ARTIFACT_BYTES = 2 * 1024 * 1024
JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")

def runs_root_for(bootloops_root: str | Path) -> Path:
    bl = Path(bootloops_root).expanduser().resolve()
    return Path(os.environ.get("BOOTLOOPS_LAB_RUNS", str(bl.parent / "bootloops-lab" / "runs"))).resolve()

def safe_job_dir(bootloops_root: str | Path, job_id: str) -> Path:
    if not JOB_ID_RE.fullmatch(job_id):
        raise ValueError("invalid job_id")
    root = runs_root_for(bootloops_root)
    job = (root / job_id).resolve()
    if job.parent != root:
        raise ValueError("job_id escaped runs root")
    if not job.is_dir():
        raise FileNotFoundError(f"job not found: {job_id}")
    return job

def list_artifacts(bootloops_root: str | Path, job_id: str) -> list[dict[str, Any]]:
    job = safe_job_dir(bootloops_root, job_id)
    return [
        {"name": p.relative_to(job).as_posix(), "size_bytes": p.stat().st_size, "sha256": sha256_file(p)}
        for p in sorted(job.rglob("*")) if p.is_file()
    ]

def read_artifact(bootloops_root: str | Path, job_id: str, name: str, max_bytes: int = MAX_ARTIFACT_BYTES) -> dict[str, Any]:
    job = safe_job_dir(bootloops_root, job_id)
    p = (job / name).resolve()
    if not name or Path(name).is_absolute() or (p != job and job not in p.parents):
        raise ValueError("artifact path not allowed")
    if not p.is_file():
        raise FileNotFoundError(f"artifact not found: {name}")
    raw = p.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"artifact exceeds {max_bytes} byte cap")
    digest = hashlib.sha256(raw).hexdigest()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"name": p.relative_to(job).as_posix(), "size_bytes": len(raw), "sha256": digest, "encoding": "binary"}
    return {"name": p.relative_to(job).as_posix(), "size_bytes": len(raw), "sha256": digest, "encoding": "utf-8", "content": content}

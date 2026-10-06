from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import safe_job_dir
from .receipt import SCHEMA, sha256_file

ALLOWED = {"PASS", "REFUSED (by design)", "FAIL", "PROCESS_TIMEOUT", "PROCESS_ERROR", "UNKNOWN"}

def verify_receipt(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    record = json.loads(p.read_text(encoding="utf-8"))
    errors: list[str] = []
    if record.get("schema") != SCHEMA: errors.append("schema mismatch")
    if not record.get("job_id"): errors.append("missing job_id")
    if record.get("status") not in ALLOWED: errors.append("invalid status")
    stdout = p.parent / "stdout.log"
    if record.get("stdout_sha256") and (not stdout.is_file() or sha256_file(stdout) != record["stdout_sha256"]):
        errors.append("stdout hash mismatch or missing")
    result = p.parent / "selftest_results.json"
    if record.get("result_sha256") and (not result.is_file() or sha256_file(result) != record["result_sha256"]):
        errors.append("result hash mismatch or missing")
    return {"schema":"scg-hcws-bootloops-verification-v1","valid":not errors,"job_id":record.get("job_id"),"package":record.get("package"),"status":record.get("status"),"errors":errors}

def verify_job(bootloops_root: str | Path, job_id: str) -> dict[str, Any]:
    return verify_receipt(safe_job_dir(bootloops_root, job_id) / "receipt.json")

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .artifacts import safe_job_dir
from .receipt import SCHEMA, sha256_file

ALLOWED = {"PASS", "REFUSED (by design)", "FAIL", "PROCESS_TIMEOUT", "PROCESS_ERROR", "UNKNOWN"}
ACCEPTED = {"PASS", "REFUSED (by design)"}


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "gateway" / "registry.yaml"


def _schema() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "schemas" / "scg-hcws-bootloops-receipt-v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_bootloops_ref() -> str:
    path = REGISTRY_PATH
    return str((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("bootloops_ref", ""))


def _result_status(record: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("status") != record.get("status"):
        errors.append("receipt status disagrees with selftest_results.json")
    if result.get("class") != record.get("verification_class"):
        errors.append("receipt verification_class disagrees with selftest_results.json")
    recorded_result = record.get("result")
    if recorded_result != result:
        errors.append("receipt result payload disagrees with selftest_results.json")
    return errors


def verify_receipt(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    errors: list[str] = []
    try:
        record = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "schema": "scg-hcws-bootloops-verification-v1",
            "integrity_ok": False,
            "acceptance_ok": False,
            "valid": False,
            "job_id": None,
            "package": None,
            "status": None,
            "errors": [f"invalid receipt JSON: {exc}"],
        }

    schema_errors = sorted(Draft202012Validator(_schema()).iter_errors(record), key=lambda e: list(e.path))
    errors.extend("schema validation: " + ("/".join(map(str, e.path)) or "<root>") + ": " + e.message for e in schema_errors)

    status = record.get("status")
    if status not in ALLOWED:
        errors.append("invalid status")

    stdout = p.parent / "stdout.log"
    stdout_hash = record.get("stdout_sha256")
    if not isinstance(stdout_hash, str) or not stdout_hash:
        errors.append("missing stdout_sha256")
    elif not stdout.is_file() or sha256_file(stdout) != stdout_hash:
        errors.append("stdout hash mismatch or missing file")

    result_path = p.parent / "selftest_results.json"
    result_hash = record.get("result_sha256")
    result_payload = None
    if status in ACCEPTED:
        if not isinstance(result_hash, str) or not result_hash:
            errors.append("accepted status requires result_sha256")
        if not result_path.is_file():
            errors.append("accepted status requires selftest_results.json")
        else:
            actual_hash = sha256_file(result_path)
            if actual_hash != result_hash:
                errors.append("result hash mismatch")
            try:
                all_results = json.loads(result_path.read_text(encoding="utf-8"))
                result_payload = all_results.get(record.get("package"))
                if not isinstance(result_payload, dict):
                    errors.append("package result missing from selftest_results.json")
                else:
                    errors.extend(_result_status(record, result_payload))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid selftest_results.json: {exc}")
    elif result_hash:
        if not result_path.is_file() or sha256_file(result_path) != result_hash:
            errors.append("result hash mismatch or missing file")
        elif isinstance(record.get("result"), dict):
            try:
                all_results = json.loads(result_path.read_text(encoding="utf-8"))
                result_payload = all_results.get(record.get("package"))
                if result_payload != record.get("result"):
                    errors.append("receipt result payload disagrees with selftest_results.json")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid selftest_results.json: {exc}")

    expected_ref = _registry_bootloops_ref()
    if record.get("bootloops_ref") != expected_ref:
        errors.append("bootloops_ref does not match registry.yaml")

    if record.get("bootloops_worktree_clean_before") is not True:
        errors.append("BootLoops worktree was not clean before execution")
    if record.get("bootloops_worktree_clean_after") is not True:
        errors.append("BootLoops worktree is not clean after execution")

    integrity_ok = not errors
    acceptance_ok = integrity_ok and status in ACCEPTED
    return {
        "schema": "scg-hcws-bootloops-verification-v1",
        "integrity_ok": integrity_ok,
        "acceptance_ok": acceptance_ok,
        "valid": integrity_ok and acceptance_ok,
        "job_id": record.get("job_id"),
        "package": record.get("package"),
        "status": status,
        "errors": errors,
    }


def verify_job(bootloops_root: str | Path, job_id: str) -> dict[str, Any]:
    return verify_receipt(safe_job_dir(bootloops_root, job_id) / "receipt.json")

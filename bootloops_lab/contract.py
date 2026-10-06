from __future__ import annotations

from typing import Final

API_SCHEMA: Final = "scg-hcws-bootloops-api-v1"
RECEIPT_SCHEMA: Final = "scg-hcws-bootloops-receipt-v1"
DEFAULT_TIMEOUT: Final = 300
MAX_TIMEOUT: Final = 1200
OPERATIONS: Final = ("catalog", "resident", "guide", "run", "verify", "artifacts", "artifact")
STATUSES: Final = ("PASS", "REFUSED (by design)", "FAIL", "PROCESS_TIMEOUT", "PROCESS_ERROR", "UNKNOWN")

def validate_operation(operation: str) -> None:
    if operation not in OPERATIONS:
        raise ValueError(f"unsupported operation: {operation}")

def validate_timeout(timeout: int) -> int:
    if not isinstance(timeout, int) or not 1 <= timeout <= MAX_TIMEOUT:
        raise ValueError(f"timeout must be between 1 and {MAX_TIMEOUT}")
    return timeout

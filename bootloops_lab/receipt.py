from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "scg-hcws-bootloops-receipt-v1"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())

def write_receipt(path: str | Path, record: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    p.write_text(payload, encoding="utf-8")

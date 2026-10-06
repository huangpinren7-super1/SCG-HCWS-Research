from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROFILE = Path(__file__).resolve().parents[1] / "bootloops-lab" / "local" / "resident-tools.yaml"

def load_resident_profile(path: str | Path = PROFILE) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"resident profile not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if data.get("schema") != "scg-hcws-resident-profile-v2":
        raise ValueError("unsupported resident profile schema")
    return data

def resident_packages(data: dict[str, Any] | None = None) -> list[str]:
    data = data or load_resident_profile()
    out: set[str] = set()
    for names in data.get("tiers", {}).values():
        out.update(names or [])
    return sorted(out)

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .profile import resident_packages

def resolve_root(root: str | Path) -> Path:
    p = Path(root).expanduser().resolve()
    if not (p / "run_selftests.py").is_file():
        raise FileNotFoundError(f"BootLoops root is not valid: {p}")
    return p

def load_catalog(root: str | Path) -> dict[str, dict[str, Any]]:
    root = resolve_root(root)
    manifest = json.loads((root / "tools" / "BATTERIES.json").read_text(encoding="utf-8"))
    classes: dict[str, str] = {}
    for line in (root / "tools" / "README.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*[\x60]([A-Za-z0-9_.-]+)/[\x60]\s*\|.*\|\s*([a-z-]+)", line)
        if m:
            classes[m.group(1)] = m.group(2)
    resident = set(resident_packages())
    return {
        name: {
            "package": name,
            "verification_class": classes.get(name, "unknown"),
            "command": spec.get("cmd"),
            "cwd": spec.get("cwd", "root"),
            "serial": bool(spec.get("serial")),
            "guide": str(root / "tools" / name / "GUIDE.md"),
            "has_project_toml": (root / "tools" / name / "Project.toml").is_file(),
            "resident": name in resident,
        }
        for name, spec in sorted(manifest.items())
    }

def read_guide(root: str | Path, package: str) -> str:
    p = resolve_root(root) / "tools" / package / "GUIDE.md"
    if not p.is_file():
        raise KeyError(f"No GUIDE.md for package: {package}")
    return p.read_text(encoding="utf-8")

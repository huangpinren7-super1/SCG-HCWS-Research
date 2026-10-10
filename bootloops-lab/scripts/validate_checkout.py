#!/usr/bin/env python3
"""Validate the pinned BootLoops checkout and record source provenance."""
from __future__ import annotations
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_checkout.py CHECKOUT EXPECTED_SHA", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    expected = sys.argv[2].strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        print("ERROR: bootloops_ref must be a full 40-character commit SHA", file=sys.stderr)
        return 2

    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    if actual != expected:
        print(f"ERROR: expected BootLoops {expected}, checked out {actual}", file=sys.stderr)
        return 1

    tools = root / "tools"
    manifest_path = tools / "BATTERIES.json"
    index_path = tools / "README.md"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package_dirs = {
        p.name for p in tools.iterdir()
        if p.is_dir() and p.name != "fixtures"
    }
    manifest_names = set(manifest)
    if len(manifest_names) != 49:
        print(f"ERROR: expected 49 battery entries, found {len(manifest_names)}", file=sys.stderr)
        return 1
    if manifest_names != package_dirs:
        print(
            "ERROR: package directory/manifest mismatch; "
            f"missing directories={sorted(manifest_names-package_dirs)}, "
            f"unregistered directories={sorted(package_dirs-manifest_names)}",
            file=sys.stderr,
        )
        return 1

    index_text = index_path.read_text(encoding="utf-8")
    indexed = set(re.findall(r"^\| `([A-Za-z0-9_.-]+)/` \|", index_text, re.M))
    if indexed != manifest_names:
        print(
            "ERROR: tools/README.md index does not match BATTERIES.json; "
            f"missing={sorted(manifest_names-indexed)}, extra={sorted(indexed-manifest_names)}",
            file=sys.stderr,
        )
        return 1

    evidence = {
        "schema": "bootloops-lab-environment-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "bootloops_commit": actual,
        "expected_commit": expected,
        "package_count": len(manifest_names),
        "battery_manifest_sha256": sha256(manifest_path),
        "tool_index_sha256": sha256(index_path),
        "python_runtime": sys.version,
        "platform": platform.platform(),
    }
    Path("bootloops-lab-env.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(evidence, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

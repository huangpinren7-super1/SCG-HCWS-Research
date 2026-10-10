#!/usr/bin/env python3
"""Emit a readable Markdown summary from BootLoops selftest_results.json."""
from __future__ import annotations
import json
import sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_selftests.py RESULTS.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    print("# BootLoops-Lab acceptance summary\n")
    if not path.is_file():
        print("No selftest_results.json was produced. See the workflow log for the setup error.")
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not parse selftest results: {type(exc).__name__}: {exc}")
        return 0

    counts: dict[str, int] = {}
    for row in data.values():
        status = str(row.get("status", "UNKNOWN"))
        counts[status] = counts.get(status, 0) + 1
    print("| Status | Count |")
    print("|---|---:|")
    for status, count in sorted(counts.items()):
        print(f"| {status} | {count} |")
    print("\n## Per-package results\n")
    print("| Package | Class | Status | Seconds |")
    print("|---|---|---|---:|")
    for package, row in sorted(data.items()):
        cls = row.get("class", "UNKNOWN")
        status = row.get("status", "UNKNOWN")
        seconds = row.get("wall_s", row.get("secs", ""))
        print(f"| {package} | {cls} | {status} | {seconds} |")
    print(f"\nTotal recorded packages: {len(data)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

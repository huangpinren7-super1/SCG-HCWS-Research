#!/usr/bin/env python3
"""Strict gate: require one result per upstream package and no undeclared failures."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ALLOWED = {"PASS", "REFUSED (by design)"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--expected", type=int, default=49)
    args = ap.parse_args()
    path = Path(args.results)
    if not path.is_file():
        print(f"FAIL: results file missing: {path}", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: invalid JSON: {exc}", file=sys.stderr)
        return 1

    counts = Counter(str(row.get("status", "UNKNOWN")) for row in data.values())
    print(json.dumps({"recorded": len(data), "expected": args.expected, "counts": dict(counts)}, indent=2))
    problems = []
    if len(data) != args.expected:
        problems.append(f"expected {args.expected} package results, got {len(data)}")
    for package, row in sorted(data.items()):
        status = str(row.get("status", "UNKNOWN"))
        if status not in ALLOWED:
            problems.append(f"{package}: status={status}")
    if problems:
        print("STRICT ACCEPTANCE GATE: FAIL", file=sys.stderr)
        for problem in problems:
            print(f" - {problem}", file=sys.stderr)
        return 1
    print("STRICT ACCEPTANCE GATE: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

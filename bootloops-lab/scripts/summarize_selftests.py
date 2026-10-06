#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "selftest_results.json")
d = json.loads(p.read_text(encoding="utf-8"))

status_counts = Counter(r.get("status", "UNKNOWN") for r in d.values())
class_status = Counter((r.get("class", "unknown"), r.get("status", "UNKNOWN")) for r in d.values())

print("# BootLoops-Lab acceptance summary")
print("")
print("| Verification class | Status | Count |")
print("|---|---|---:|")
for (cls, status), count in sorted(class_status.items()):
    print(f"| `{cls}` | `{status}` | {count} |")

print("")
print("## Status totals")
print("")
print("| Status | Count |")
print("|---|---:|")
for status, count in sorted(status_counts.items()):
    print(f"| `{status}` | {count} |")

print("")
print("## Packages")
print("")
print("| Package | Verification class | Status | Time (s) |")
print("|---|---|---|---:|")
for name, r in sorted(d.items()):
    secs = r.get("secs", r.get("wall_s", ""))
    print(f"| `{name}` | `{r.get('class', 'unknown')}` | **{r.get('status', 'UNKNOWN')}** | {secs} |")

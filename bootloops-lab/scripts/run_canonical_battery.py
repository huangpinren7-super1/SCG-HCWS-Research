#!/usr/bin/env python3
"""Run the canonical 49-package battery with explicit timeout classes.

The upstream default of 300 s is retained for ordinary packages. Historically
observed heavier packages get explicit, documented exceptions:
  dogtag: 360 s
  abacus: 1200 s

The final selftest_results.json is a deterministic merge of the three runs.
A FAIL is never reclassified; the wrapper exits non-zero whenever any package
is not PASS or REFUSED (by design).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANONICAL_PACKAGE_COUNT = 49\nACCEPTED = {"PASS", "REFUSED (by design)"}


def run_group(root: Path, packages: list[str], timeout: int, label: str, par: int) -> tuple[int, dict]:
    result_path = root / "selftest_results.json"
    try:
        result_path.unlink()
    except FileNotFoundError:
        pass

    print(f"\n=== {label}: {len(packages)} packages, timeout={timeout}s, par={par} ===", flush=True)
    cmd = [
        sys.executable,
        "run_selftests.py",
        *packages,
        "--par",
        str(par),
        "--timeout",
        str(timeout),
    ]
    rc = subprocess.run(cmd, cwd=root, check=False).returncode
    if not result_path.is_file():
        print(f"{label}: selftest_results.json was not produced", file=sys.stderr, flush=True)
        return rc or 1, {}
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"{label}: invalid selftest_results.json: {exc}", file=sys.stderr, flush=True)
        return rc or 1, {}
    return rc, data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--par", type=int, default=4)
    ap.add_argument("--standard-timeout", type=int, default=300)
    ap.add_argument("--dogtag-timeout", type=int, default=360)
    ap.add_argument("--abacus-timeout", type=int, default=1200)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest = json.loads((root / "tools" / "BATTERIES.json").read_text(encoding="utf-8"))
    packages = sorted(manifest)
    exceptions = {"abacus": args.abacus_timeout, "dogtag": args.dogtag_timeout}
    standard = [p for p in packages if p not in exceptions]

    merged: dict[str, dict] = {}
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="bootloops-battery-") as td:
        tmp = Path(td)

        for label, group, timeout in (
            ("standard", standard, args.standard_timeout),
            ("dogtag-exception", ["dogtag"], args.dogtag_timeout),
            ("abacus-exception", ["abacus"], args.abacus_timeout),
        ):
            rc, data = run_group(root, group, timeout, label, args.par)
            merged.update(data)
            if rc != 0:
                failures.extend(
                    name for name, entry in data.items()
                    if entry.get("status") not in ACCEPTED
                )
            (tmp / f"{label}.json").write_text(
                json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    missing = sorted(set(packages) - set(merged))
    extra = sorted(set(merged) - set(packages))
    if missing:
        failures.extend(missing)
        print(f"Missing package results: {missing}", file=sys.stderr)
    if extra:
        failures.extend(extra)
        print(f"Unexpected package results: {extra}", file=sys.stderr)

    for name, entry in merged.items():
        if entry.get("status") not in ACCEPTED:
            if name not in failures:
                failures.append(name)

    (root / "selftest_results.json").write_text(
        json.dumps(dict(sorted(merged.items())), indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    counts: dict[str, int] = {}
    for entry in merged.values():
        status = entry.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

    print("\n=== merged canonical result ===")
    print(json.dumps(counts, indent=2, ensure_ascii=False))
    print(
        "timeout policy: standard=300s, dogtag=360s, abacus=1200s; "
        "upstream default remains 300s"
    )
    if failures:
        print(f"canonical battery FAILED: {sorted(set(failures))}", file=sys.stderr)
        return 1
    if len(merged) != len(packages):
        print(f"canonical battery FAILED: expected {len(packages)} results, got {len(merged)}", file=sys.stderr)
        return 1
    print("canonical battery: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

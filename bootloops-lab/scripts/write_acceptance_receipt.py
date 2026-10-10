#!/usr/bin/env python3
"""Emit a provenance-bound receipt for the 49-package canonical battery."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / "gateway" / "registry.yaml"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(root: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--research-ref", default=os.environ.get("GITHUB_SHA", ""))
    ap.add_argument("--ci-run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    ap.add_argument("--par", type=int, default=4)
    ap.add_argument("--standard-timeout", type=int, default=300)
    ap.add_argument("--dogtag-timeout", type=int, default=360)
    ap.add_argument("--abacus-timeout", type=int, default=1200)
    ap.add_argument("--holonomic-timeout", type=int, default=1200)
    ap.add_argument("--require-accepted", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    result_path = Path(args.result).resolve()
    out_path = Path(args.out).resolve()

    import yaml
    registry_data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    expected_ref = str(registry_data.get("bootloops_ref", ""))
    actual_ref = git(root, "rev-parse", "HEAD")
    manifest = json.loads((root / "tools" / "BATTERIES.json").read_text(encoding="utf-8"))
    expected_packages = set(manifest)
    status_lines = [x for x in git(root, "status", "--porcelain", "--untracked-files=all").splitlines() if x.strip()]
    unexpected = [x for x in status_lines if (x[3:] if len(x) >= 3 else x) != "selftest_results.json"]

    receipt: dict = {
        "schema": "scg-hcws-bootloops-acceptance-receipt-v1",
        "ci": {
            "provider": "github-actions",
            "run_id": args.ci_run_id or None,
            "research_ref": args.research_ref or None,
        },
        "bootloops": {
            "root": str(root),
            "expected_ref": expected_ref,
            "actual_ref": actual_ref,
            "ref_matches_registry": actual_ref == expected_ref,
            "worktree_clean": not unexpected,
            "unexpected_worktree_changes": unexpected,
        },
        "parameters": {
            "canonical_package_count": 49,
            "par": args.par,
            "standard_timeout_seconds": args.standard_timeout,
            "dogtag_timeout_seconds": args.dogtag_timeout,
            "abacus_timeout_seconds": args.abacus_timeout,
            "holonomic_timeout_seconds": args.holonomic_timeout,
        },
        "result_file": str(result_path),
        "result_sha256": sha256_file(result_path) if result_path.is_file() else None,
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
        },
    }

    if result_path.is_file():
        data = json.loads(result_path.read_text(encoding="utf-8"))
        status_counts = Counter(v.get("status", "UNKNOWN") for v in data.values())
        class_counts = Counter(v.get("class", "unknown") for v in data.values())
        receipt["result_count"] = len(data)
        receipt["status_counts"] = dict(sorted(status_counts.items()))
        receipt["verification_class_counts"] = dict(sorted(class_counts.items()))
        receipt["package_statuses"] = {k: v.get("status", "UNKNOWN") for k, v in sorted(data.items())}
        receipt["package_classes"] = {k: v.get("class", "unknown") for k, v in sorted(data.items())}
        receipt["accepted"] = (
            len(data) == len(expected_packages)
            and set(data) == expected_packages
            and set(status_counts).issubset({"PASS", "REFUSED (by design)"})
            and actual_ref == expected_ref
            and not unexpected
        )
    else:
        receipt["result_count"] = 0
        receipt["status_counts"] = {}
        receipt["verification_class_counts"] = {}
        receipt["accepted"] = False
        receipt["error"] = "selftest_results.json was not produced"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if (receipt["accepted"] or not args.require_accepted) else 1


if __name__ == "__main__":
    raise SystemExit(main())

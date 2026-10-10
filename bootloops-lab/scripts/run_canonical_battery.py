#!/usr/bin/env python3
"""Run the canonical 49-package battery with explicit timeout classes.

The upstream default of 300 s is retained for ordinary packages. Packages
with engine-level long-running work get explicit exceptions:
  dogtag: 360 s
  abacus: 1200 s
  holonomic: 1200 s

The holonomic smoke runs under Sage/FLINT and must not inherit the temporary
FiniteFlow/Blade dynamic-library search paths used by the separate Blade
preflight. Its mathematical gates remain mandatory; the timeout only bounds
execution and never converts FAIL to PASS.

The final selftest_results.json is a deterministic merge of the three runs.
A FAIL is never reclassified; the wrapper exits non-zero whenever any package
is not PASS or REFUSED (by design).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CANONICAL_PACKAGE_COUNT = 49
ACCEPTED = {"PASS", "REFUSED (by design)"}


def run_group(root: Path, packages: list[str], timeout: int, label: str, par: int, env: dict[str, str]) -> tuple[int, dict]:
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
    rc = subprocess.run(cmd, cwd=root, env=env, check=False).returncode
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
    ap.add_argument("--holonomic-timeout", type=int, default=1200)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest = json.loads((root / "tools" / "BATTERIES.json").read_text(encoding="utf-8"))
    packages = sorted(manifest)
    if len(packages) != CANONICAL_PACKAGE_COUNT:
        raise RuntimeError(
            f"canonical manifest drift: expected {CANONICAL_PACKAGE_COUNT} packages, got {len(packages)}"
        )
    exceptions = {
        "abacus": args.abacus_timeout,
        "dogtag": args.dogtag_timeout,
        "holonomic": args.holonomic_timeout,
    }
    standard = [p for p in packages if p not in exceptions]

    merged: dict[str, dict] = {}
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="bootloops-battery-") as td:
        tmp = Path(td)
        shim_dir = tmp / "python-shims"
        shim_dir.mkdir()
        for name in ("python", "python3"):
            shim = shim_dir / name
            shim.write_text(
                "#!/usr/bin/env bash\n"
                f'exec {json.dumps(sys.executable)} "$@"\n',
                encoding="utf-8",
            )
            shim.chmod(0o755)
        child_env = dict(os.environ)
        child_env["PATH"] = f"{shim_dir}:{child_env.get('PATH', '')}"

        # Restore the pre-Blade loader path for SageMath/FLINT. Blade's
        # private library directories are needed by Blade executables but must
        # not shadow libraries used by the independent holonomic engine.
        holonomic_env = dict(child_env)
        base_ld_library_path = holonomic_env.get("RESEARCH_BASE_LD_LIBRARY_PATH")
        if base_ld_library_path is not None:
            if base_ld_library_path:
                holonomic_env["LD_LIBRARY_PATH"] = base_ld_library_path
            else:
                holonomic_env.pop("LD_LIBRARY_PATH", None)
        else:
            loader_paths = holonomic_env.get("LD_LIBRARY_PATH", "").split(os.pathsep)
            clean_paths = [
                path for path in loader_paths
                if path
                and "/vendor/blade/lib" not in path
                and "/finiteflow/lib" not in path
            ]
            if clean_paths:
                holonomic_env["LD_LIBRARY_PATH"] = os.pathsep.join(clean_paths)
            else:
                holonomic_env.pop("LD_LIBRARY_PATH", None)
        print(
            "[holonomic isolated environment] LD_LIBRARY_PATH="
            + holonomic_env.get("LD_LIBRARY_PATH", "<unset>"),
            flush=True,
        )

        for label, group, timeout, group_env in (
            ("standard", standard, args.standard_timeout, child_env),
            ("dogtag-exception", ["dogtag"], args.dogtag_timeout, child_env),
            ("abacus-exception", ["abacus"], args.abacus_timeout, child_env),
            ("holonomic-exception", ["holonomic"], args.holonomic_timeout, holonomic_env),
        ):
            rc, data = run_group(root, group, timeout, label, args.par, group_env)
            merged.update(data)
            if rc != 0:
                failures.append(f"{label}: upstream run_selftests exited {rc}")
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
        "timeout policy: standard=300s, dogtag=360s, abacus=1200s, "
        "holonomic=1200s; upstream default remains 300s"
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

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BOOTLOOPS_VENV:-$ROOT/.venv}/bin/python"
[ -x "$PY" ] || PY=python3

if [ -n "${BOOTLOOPS_ROOT:-}" ]; then
  BL="$BOOTLOOPS_ROOT"
elif [ -d "$ROOT/vendor/bootloops" ]; then
  BL="$ROOT/vendor/bootloops"
else
  echo "BootLoops checkout not found. Set BOOTLOOPS_ROOT or place it at vendor/bootloops." >&2
  exit 2
fi

echo "== BootLoops-Lab local environment doctor =="
echo "Python: $($PY --version 2>&1)"

"$PY" - <<'PY'
from importlib.metadata import version
import importlib
import sys

expected = {
    "pip": "26.2.1",
    "setuptools": "84.0.0",
    "wheel": "0.48.0",
    "mpmath": "1.3.0",
    "sympy": "1.14.0",
    "numpy": "2.4.6",
    "scipy": "1.16.3",
    "python-flint": "0.9.0",
    "gmpy2": "2.3.2",
    "pyyaml": "6.0.3",
    "jsonschema": "4.26.0",
    "networkx": "3.6.1",
    "dynesty": "3.1.0",
    "cypari2": "2.2.2",
    "msprime": "1.4.4",
    "tskit": "1.0.3",
    "moments-popgen": "1.6.1",
    "pySecDec": "1.6.6",
    "pytest": "9.1.1",
}
imports = {
    "mpmath": "mpmath",
    "sympy": "sympy",
    "numpy": "numpy",
    "scipy": "scipy",
    "python-flint": "flint",
    "gmpy2": "gmpy2",
    "pyyaml": "yaml",
    "jsonschema": "jsonschema",
    "networkx": "networkx",
    "dynesty": "dynesty",
    "cypari2": "cypari2",
    "msprime": "msprime",
    "tskit": "tskit",
}
errors = []
for dist, want in expected.items():
    try:
        got = version(dist)
    except Exception as exc:
        errors.append(f"{dist}: not installed ({exc})")
        continue
    if got != want:
        errors.append(f"{dist}: expected {want}, got {got}")
    else:
        print(f"PYTHON {dist}=={got}: PASS")
for label, mod in imports.items():
    try:
        importlib.import_module(mod)
        print(f"IMPORT {label}: PASS")
    except Exception as exc:
        errors.append(f"import {label}: {exc}")
if errors:
    for err in errors:
        print("ERROR:", err)
    raise SystemExit(1)
print(f"Python version: {sys.version.split()[0]}")
PY

"$PY" - <<PY
from bootloops_lab.runner import bootloops_fingerprint
fp = bootloops_fingerprint("$BL")
assert fp["ref_matches_registry"], fp
assert fp["worktree_clean"], fp
print("BOOTLOOPS ref:", fp["actual_ref"])
print("BOOTLOOPS provenance/worktree: PASS")
PY

COUNT="$("$PY" -m bootloops_lab.cli --bootloops-root "$BL" catalog | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)))')"
test "$COUNT" -eq 49
echo "CATALOG 49-package surface: PASS"

"$PY" -m bootloops_lab.cli --bootloops-root "$BL" resident >/dev/null
echo "Resident profile: PASS"

for cmd in gp gphelp msolve Singular julia sage; do
  command -v "$cmd" >/dev/null
  echo "ENGINE $cmd: PASS ($(command -v "$cmd"))"
done

for hdr in /usr/include/flint/flint.h /usr/include/ginac/ginac.h; do
  test -f "$hdr"
  echo "HEADER $hdr: PASS"
done

if [ -n "${BLADE_BIN_DIR:-}" ]; then
  for exe in redg1 fitrel fflowcli dumppoints; do
    test -x "${BLADE_BIN_DIR}/$exe"
    echo "ENGINE Blade $exe: PASS"
  done
else
  echo "ENGINE Blade binaries: SKIPPED (BLADE_BIN_DIR not set in this shell)"
fi

echo "BootLoops-Lab local environment doctor: PASS"

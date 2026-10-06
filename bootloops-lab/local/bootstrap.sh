#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${BOOTLOOPS_VENV:-$ROOT/.venv}"
REQ="$ROOT/bootloops-lab/local/requirements-core.txt"

if [ -n "${BOOTLOOPS_ROOT:-}" ]; then
  BL="$BOOTLOOPS_ROOT"
elif [ -d "$ROOT/vendor/bootloops" ]; then
  BL="$ROOT/vendor/bootloops"
else
  echo "BootLoops checkout not found. Set BOOTLOOPS_ROOT or place it at vendor/bootloops." >&2
  exit 2
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV/bin/python" -m pip install -r "$REQ"

cat > "$ROOT/bootloops-lab/local/environment.local" <<EOF
export BOOTLOOPS_ROOT="$BL"
export PATH="$VENV/bin:\$PATH"
EOF

echo "BootLoops-Lab local resident layer: READY"
echo "BootLoops: $BL"
echo "Python venv: $VENV"
"$VENV/bin/python" -m bootloops_lab.cli --bootloops-root "$BL" catalog >/dev/null
echo "Catalog probe: PASS"
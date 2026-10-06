#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${BOOTLOOPS_VENV:-$ROOT/.venv}"
REQ="$ROOT/bootloops-lab/local/requirements-core.txt"
TOOLING_REQ="$ROOT/bootloops-lab/local/requirements-tooling.txt"

if [ -n "${BOOTLOOPS_ROOT:-}" ]; then
  BL="$BOOTLOOPS_ROOT"
elif [ -d "$ROOT/vendor/bootloops" ]; then
  BL="$ROOT/vendor/bootloops"
else
  echo "BootLoops checkout not found. Set BOOTLOOPS_ROOT or place it at vendor/bootloops." >&2
  exit 2
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --disable-pip-version-check -r "$TOOLING_REQ"
"$VENV/bin/python" -m pip install --disable-pip-version-check -r "$REQ"

if [ "${1:-}" = "--with-mcp" ]; then
  "$VENV/bin/python" -m pip install --disable-pip-version-check -r "$ROOT/bootloops-lab/local/requirements-mcp.txt"
fi

cat > "$ROOT/bootloops-lab/local/environment.local" <<EOF
export BOOTLOOPS_ROOT="$BL"
export BOOTLOOPS_VENV="$VENV"
export BOOTLOOPS_REF="66b680ce742e654cfe86da4f072a69061fe182b1"
export PATH="$VENV/bin:\$PATH"
EOF

"$VENV/bin/python" -m bootloops_lab.cli --bootloops-root "$BL" catalog >/dev/null
"$VENV/bin/python" -m bootloops_lab.cli --bootloops-root "$BL" resident >/dev/null
"$ROOT/bootloops-lab/local/doctor.sh"
echo "BootLoops-Lab resident layer: READY"
echo "Use --with-mcp to install the optional MCP transport."

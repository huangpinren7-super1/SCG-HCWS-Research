#!/usr/bin/env bash
set -u

echo '== BootLoops-Lab local environment doctor ==' 
echo "Python: $(python3 --version 2>&1 || true)"
for mod in mpmath sympy numpy scipy flint gmpy2 yaml networkx dynesty cypari2 msprime tskit; do
  if python3 -c "import $mod" >/dev/null 2>&1; then
    echo "PYTHON $mod: PASS"
  else
    echo "PYTHON $mod: MISSING"
  fi
done
for cmd in gp gphelp msolve Singular julia sage; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "ENGINE $cmd: PASS ($(command -v "$cmd"))"
  else
    echo "ENGINE $cmd: MISSING"
  fi
done
for hdr in /usr/include/flint/flint.h /usr/include/ginac/ginac.h; do
  if [ -f "$hdr" ]; then echo "HEADER $hdr: PASS"; else echo "HEADER $hdr: MISSING"; fi
done
if [ -n "${BLADE_BIN_DIR:-}" ] && [ -x "${BLADE_BIN_DIR}/redg1" ]; then
  echo "ENGINE Blade/redg1: PASS"
else
  echo "ENGINE Blade/redg1: MISSING"
fi
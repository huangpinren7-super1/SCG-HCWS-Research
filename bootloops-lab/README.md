# BootLoops-Lab

Integration layer between SCG-HCWS research and upstream BootLoops.

Upstream code is never modified by this lab. The cloud workflow checks out an explicit BootLoops commit.

## Layout
- .github/workflows/bootloops.yml — full 49-package canonical acceptance.
- .github/workflows/abacus-rescue.yml — isolated abacus run with 1200 s timeout.
- .github/workflows/lab-smoke.yml — fast infrastructure/interface smoke only.
- bootloops-lab/local/ — resident local environment and engine profile.
- bootloops_lab/ — standardized Python catalog, guide, acceptance and receipt API.
- gateway/ — allowlisted local Gateway and optional MCP stdio transport.
- experiments/ — SCG/HCWS computations.
- certificates/ — frozen computational evidence.

## Verification levels
Installed -> Battery PASS -> REFUSED (by design) -> FAIL. A FAIL is never reclassified by interpretation.

## Current infrastructure policy
The 49-package baseline remains pinned to BootLoops 1.0 SHA 66b680ce742e654cfe86da4f072a69061fe182b1.
The cloud battery now provisions FLINT C headers, GiNaC, msolve, Singular, pySecDec, and attempts SageMath 10.7.
Reference-sensitive data are never fabricated. Missing CLINCH, Eichler, Galois or Blade replay banks remain fail-closed.
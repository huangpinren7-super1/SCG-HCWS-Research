# BootLoops-Lab Engine Lanes

## System mathematics lane
- PARI/GP: pari-gp, pari-doc, libpari-dev
- FLINT C development: libflint-dev
- GiNaC/CLN development: libginac-dev
- polynomial engines: msolve and Singular
- GMP/MPFR/MP C development libraries

These are intended to arm the previously skipped higher-level tests in gpl-eval,
posq, landau-alphabet and dipstick.

## Python lane
- python-flint 0.9.0
- cypari2 2.2.2
- pySecDec 1.6.6
- common NumPy/SciPy/SymPy/mpmath stack

## Julia/Sage lane
CI provisions Julia 1.11 and attempts SageMath 10.7 via conda-forge,
with ore_algebra 0.5 installed inside the Sage environment.

## Blade lane
CI makes a best-effort build of the pinned BootLoops Blade fork and pinned FiniteFlow.
The resulting bin directory is exported as BLADE_BIN_DIR when the build succeeds.
The Blade regression reference bank BLADE_PORT_ROOT remains external data and is not fabricated.

## Reference-data lane
Reference/data banks are opt-in and provenance-sensitive:
- CLINCH_REFERENCE_DIR
- G2KIT_TRUE_JSON
- GALOIS_CAMPAIGN_BANK
- BLADE_PORT_ROOT

The repository only activates one when real payload files are present.

## Runner capability boundary
GitHub-hosted runners do not grant the workflow permission to create arbitrary cgroup
subdirectories. AMFlow-kit/seedling memory-limit probes may therefore continue to skip
by name. That is a platform capability limitation, not a mathematical assertion failure.
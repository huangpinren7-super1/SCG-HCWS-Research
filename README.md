# SCG-HCWS-Research

Cloud research laboratory for SCG/HCWS and reproducible quantitative science.

BootLoops is an external, pinned computational dependency.

## Current laboratory layers

- **BootLoops Acceptance** — 49-package canonical battery on Ubuntu 24.04, with the upstream 300 s default preserved for ordinary packages and explicit timeout exceptions only for historically measured heavy cases.
- **Local resident layer** — reusable Python scientific stack plus explicit engine lanes.
- **Standardized interface** — `bootloops_lab` catalog/guide/run/receipt/verify/artifact API with hash-checked evidence.
- **Gateway** — allowlisted local control plane with optional MCP stdio transport; not a sandbox.
- **Truth-injected toolchain QA** — known finite-dimensional algebra objects test the exact/mod-p linear-algebra substrate before formal SCG-HCWS computations.

## Evidence status

The current BootLoops baseline is intentionally **PROVISIONAL** until a matching Python 3.12 / Julia 1.11 / par=4 execution passes the strict baseline check. A provisional baseline cannot gate CI.

Historical Run #5 remains preserved as a real FAIL-containing record; it is not retroactively converted into an acceptance result. The later Run #9 result is the current provisional baseline source and is separately provenance-addressed.

## Research boundary

The present work is infrastructure-first. SCG/HCWS theorem proofs and claim attacks are kept outside the foundation layer. Tool mappings are hypotheses until the truth-injected benchmarks and problem-specific independent validations are green.

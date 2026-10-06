# Certificates and evidence

This directory stores **immutable, provenance-addressed computational evidence**. Historical records are never silently rewritten into current acceptance results.

- `bootloops-1.0-run5-historical-record.*` — renamed semantically in-place as a **historical superseded Run #5 record**; it contains a real `abacus` FAIL and preserves that fact.
- `bootloops-lab/config/expected-selftests.json` — current machine-readable baseline source. It is `PROVISIONAL` until a matching Python 3.12 / Julia 1.11 / par=4 run passes and it is explicitly promoted to `CONFIRMED`.
- `experiments/toolchain_truth/` — pre-research truth-injected benchmark used to validate the computational substrate and to constrain the research mapping claims.

For every accepted run, provenance should bind the research commit, actual BootLoops checkout SHA, runner/runtime versions, verification class, raw result hash, and CI artifact digest. A self-computed hash is an integrity check, not an authenticity proof; an external CI artifact, commit, or signature is the stronger anchor.

The historical Run #5 artifact was externally recorded as artifact `11400509437` with ZIP digest `51363fd...`; its extracted `selftest_results.json` digest is `02e1913536f0e808d5a0ceaf5798615e6c0589dce1e004688d5d03617e532b10`.

# BootLoops 1.0 Run #5 — Historical Run Record

> **Status: HISTORICAL-SUPERSEDED.** This file is not the current acceptance certificate and must not be used as evidence that the repository was green.

## Provenance

- BootLoops commit: `66b680ce742e654cfe86da4f072a69061fe182b1`
- Research commit: `4c8c8b4574273438198073c55a66f2429de23d28`
- GitHub Actions run: `37438820516` (Run #5)
- Workflow conclusion: `success`
- Runner: Ubuntu 24.04 / Python 3.11 / Julia 1.11
- Artifact ID: `11400509437`
- Artifact ZIP SHA-256: `51363fd943d18b226df9848bd82c067520ff67d664f823bfb6389d5373656690`
- Extracted `selftest_results.json` SHA-256: `02e1913536f0e808d5a0ceaf5798615e6c0589dce1e004688d5d03617e532b10`
- Raw result path: `certificates/historical/bootloops-1.0-run5-selftest_results.json` (the exact historical JSON should be preserved here when repository archival is performed)

## Result

| Status | Count |
|---|---:|
| PASS | 45 |
| REFUSED (by design) | 3 |
| FAIL | 1 |
| **Total** | **49** |

`abacus` was a real `FAIL` at the upstream 300 s timeout. The workflow nevertheless concluded `success` because the old workflow used `continue-on-error`. That contradiction is retained as a historical supply-chain/CI lesson; it is not repaired by changing the result.

The three data-gated refusals were `ffcapital`, `frobenius-boundary`, and `galois`.

## Relationship to the current baseline

Run #5 is superseded by the later Run #9 result (`37450608252`), which recorded 46 PASS / 3 REFUSED and became the **PROVISIONAL** source for `bootloops-lab/config/expected-selftests.json`. That baseline is intentionally non-gating until a matching Python 3.12 / Julia 1.11 / par=4 run passes the strict checker.

The historical record and the current provisional baseline are therefore separate evidence generations, not contradictory acceptance certificates.

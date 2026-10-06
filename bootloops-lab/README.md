# BootLoops-Lab

Integration layer between SCG-HCWS research and upstream BootLoops.

Upstream code is never modified by this lab. The workflow checks out an explicit BootLoops commit and stores generated reports as artifacts.

## Layout

- `.github/workflows/bootloops.yml` — cloud acceptance runner.
- `bootloops-lab/config/` — optional local engine/data configuration.
- `bootloops-lab/scripts/` — report helpers.
- `experiments/` — SCG/HCWS computations.
- `certificates/` — frozen computational evidence.

## Verification levels

Installed → Battery PASS → REFUSED (by design) → FAIL. A FAIL is never reclassified by interpretation.

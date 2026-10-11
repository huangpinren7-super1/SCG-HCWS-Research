# BootLoops-Lab foundation

This layer connects the pinned BootLoops toolkit to SCG-HCWS computational research.

## Principles

1. **Keep upstream immutable.** The CI runner checks out BootLoops into vendor/bootloops at an explicit full commit SHA. The lab never edits upstream files.
2. **Use the upstream acceptance entry point.** Run run_selftests.py across the whole tools index; do not replace its battery definitions with inferred commands.
3. **Fail closed.** The acceptance result gate requires exactly 49 records. PASS and REFUSED (by design) are the only accepted statuses; FAIL, missing entries, unexpected statuses, or absent results fail the job.
4. **Record provenance.** Keep the resolved source SHA, manifest/index hashes, Python/Julia versions, pip freeze, raw JSON, logs, and summary with each artifact.
5. **Separate environment gaps from mathematics.** Optional engines/data may lead to a declared refusal or battery failure; never relabel a failure as success by hand.

## Directory map

- .github/workflows/bootloops.yml — reproducible cloud acceptance run.
- bootloops-lab/requirements-core.txt — required Python math stack.
- bootloops-lab/requirements-pari.txt — required `cypari2` binding for the upstream `abacus` acceptance battery.
- bootloops-lab/requirements-extra-common.txt — common optional Python dependencies.
- bootloops-lab/scripts/validate_checkout.py — pin and 49-package structural audit.
- bootloops-lab/scripts/summarize_selftests.py — human-readable result table.
- bootloops-lab/scripts/check_results.py — strict count/status gate.
- experiments/ — named SCG-HCWS computational experiments.
- certificates/ — frozen verification evidence and receipts.

## Baseline choice

Initial baseline: Ubuntu 24.04, Python 3.11, Julia 1.11, default per-package timeout 300 seconds, parallelism 4. This aligns with the existing BootLoops 1.0 baseline lineage. Change versions or timeout only in a separately reviewed run.

The `abacus` selftest imports `cypari2` before entering its mathematical battery. The workflow therefore installs `pari-gp`, `pari-doc`, and `libpari-dev`, then installs and smoke-tests `cypari2` as a required dependency. In this Ubuntu baseline, `pari-doc` supplies the `gphelp` helper needed by the `cypari2` source build. A failed installation must stop the run; it must not be converted into an accepted refusal or hidden by `continue-on-error`.

## Run it

After the first commit lands, open Actions → BootLoops Acceptance Battery → Run workflow. Use the pinned SHA by default. Workflow artifacts include JSON, logs, environment provenance and a Markdown report.

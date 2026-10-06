# Toolchain truth benchmark

This directory is a **pre-research gate**. It does not test SCG or HCWS claims.

The purpose is to falsify an overly strong statement that the BootLoops `rankscreen -> winnow -> vopclose` chain is already a validated solver for finite-dimensional algebraic structure.

## Planted ground truths

| Object | Representation | Exact truth |
|---|---|---|
| `M₂(Q) ⊕ M₃(Q)` | block-diagonal defining representation on `Q⁵` | `dim Z(A)=2`, commutant in `End(Q⁵)` has dimension `2` |
| `Q[S₃]` | left-regular representation on `Q⁶` | `dim Z(Q[S₃])=3`, commutant in `End(Q⁶)` has dimension `6` |

The benchmark constructs the commutator equations itself, computes an exact-Q rank as a local oracle, and then requires `rankscreen` and `winnow` to reproduce the planted rank/nullity.

The benchmark deliberately does **not** use `vopclose` as an algebra solver. Its upstream GUIDE defines it as a 1-D path-DE closure engine. The test therefore audits that scope declaration and records `vopclose = NOT-APPLICABLE` for this task.

## Acceptance rule

All four planted systems must satisfy:

1. exact-Q rank agrees with the planted nullity;
2. `rankscreen` returns `CERTIFIED-SCREEN` with the same rank on two primes;
3. `winnow` finite-field elimination returns the same rank/nullity;
4. the `vopclose` scope guard remains present.

A failure blocks the claim that this toolchain mapping is established.

## Run

From the repository root:

    python bootloops-lab/scripts/test_toolchain_truth.py --bootloops-root vendor/bootloops

The smoke workflow runs this benchmark on every PR/push touching the research lab, gateway, experiments, certificates, schemas, reference data, or workflows.

## Scientific status

This benchmark validates only the **computational substrate and its scope**. It does not establish any SCG-HCWS theorem, correspondence, or physical claim. The earlier mathematical mapping document must be read as a hypothesis until this gate is green and later problem-specific benchmarks are independently validated.

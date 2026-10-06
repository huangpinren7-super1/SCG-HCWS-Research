#!/usr/bin/env python3
"""Truth-injected finite-algebra QA for the BootLoops linear-algebra substrate.

This is a pre-research capability test, not an SCG/HCWS theorem test.

Ground truths:
  * M2(Q) ⊕ M3(Q): dim center = 2; dim commutant in End(Q^5) = 2.
  * Q[S3] in its left-regular representation: dim center = 3;
    dim commutant in End(Q^6) = 6.

rankscreen and winnow are tested only as exact/mod-p linear-elimination
components on the commutator systems. vopclose is explicitly audited as
NOT-APPLICABLE to center/commutant work because its upstream contract is
1-D path-DE closure, not finite-dimensional algebra.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Iterable


def mat_zero(n: int) -> list[list[int]]:
    return [[0] * n for _ in range(n)]


def mat_commutator(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    n = len(a)
    ab = [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    ba = [[sum(b[i][k] * a[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    return [[ab[i][j] - ba[i][j] for j in range(n)] for i in range(n)]


def matrix_units(n: int) -> list[list[list[int]]]:
    out = []
    for i in range(n):
        for j in range(n):
            m = mat_zero(n)
            m[i][j] = 1
            out.append(m)
    return out


def direct_sum_matrix_units(n1: int, n2: int) -> list[list[list[int]]]:
    n = n1 + n2
    out = []
    for i in range(n1):
        for j in range(n1):
            m = mat_zero(n)
            m[i][j] = 1
            out.append(m)
    for i in range(n2):
        for j in range(n2):
            m = mat_zero(n)
            m[n1 + i][n1 + j] = 1
            out.append(m)
    return out


def s3_left_regular_basis() -> list[list[list[int]]]:
    gs = list(permutations(range(3)))

    def compose(g, h):
        return tuple(g[h[i]] for i in range(3))

    index = {g: i for i, g in enumerate(gs)}
    out = []
    for g in gs:
        m = mat_zero(len(gs))
        for j, h in enumerate(gs):
            m[index[compose(g, h)]][j] = 1
        out.append(m)
    return out


def commutant_equations(ambient_basis: list[list[list[int]]],
                        constraints: Iterable[list[list[int]]]) -> list[dict[int, Fraction]]:
    rows: list[dict[int, Fraction]] = []
    for b in constraints:
        coeffs = [mat_commutator(x, b) for x in ambient_basis]
        n = len(b)
        for i in range(n):
            for j in range(n):
                row = {
                    k: Fraction(coeffs[k][i][j])
                    for k in range(len(ambient_basis))
                    if coeffs[k][i][j] != 0
                }
                if row:
                    rows.append(row)
    return rows


def exact_rank(rows: list[dict[int, Fraction]], ncols: int) -> int:
    a = [{c: Fraction(v) for c, v in r.items() if v} for r in rows]
    rank = 0
    for col in range(ncols):
        pivot = next((i for i in range(rank, len(a)) if a[i].get(col, 0)), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        lead = a[rank][col]
        a[rank] = {c: v / lead for c, v in a[rank].items()}
        for i in range(len(a)):
            if i == rank:
                continue
            f = a[i].get(col, 0)
            if f:
                for c, v in a[rank].items():
                    nv = a[i].get(c, 0) - f * v
                    if nv:
                        a[i][c] = nv
                    else:
                        a[i].pop(c, None)
        rank += 1
        if rank == len(a):
            break
    return rank


def load_bootloops(root: Path) -> Path:
    tools = root / "tools"
    if not (tools / "rankscreen" / "shim.py").is_file():
        raise FileNotFoundError(f"BootLoops tools not found under {tools}")
    sys.path.insert(0, str(tools / "rankscreen"))
    sys.path.insert(0, str(tools / "winnow"))
    return tools


def run_linear_backends(bootloops_root: Path, name: str, rows: list[dict[int, Fraction]],
                        nvars: int, expected_nullity: int, summary: dict) -> None:
    import shim
    import screen as rank_screen

    rank_q = exact_rank(rows, nvars)
    expected_rank = nvars - expected_nullity
    if rank_q != expected_rank:
        raise AssertionError(f"{name}: exact-Q rank {rank_q} != planted {expected_rank}")

    rows_all = [(f"{name}:eq{idx}", row, Fraction(0)) for idx, row in enumerate(rows)]
    screen_input = [(row, rhs) for _, row, rhs in rows_all]
    verdict = rank_screen.screen_rows(
        screen_input,
        [lab for lab, _, _ in rows_all],
        nvars,
        k=2,
        backend="auto",
        tag=name,
    )
    if not verdict["agree"] or verdict["rank"] != expected_rank:
        raise AssertionError(
            f"{name}: rankscreen mismatch: {verdict['verdict']} rank={verdict.get('rank')}"
        )

    # Winnow is used strictly as a finite-field eliminator here, not as a
    # semantic center/commutant solver. A homogeneous row system has
    # nullity = nvars - number of pivots.
    import ibplapper as lap
    prime = 1_000_003
    mod_rows = [
        {int(c): int(v.numerator * pow(v.denominator, -1, prime) % prime) for c, v in row.items()}
        for row in rows
    ]
    wsys = lap.System(mod_rows, prime, {c: c for c in range(nvars)}, forbid=())
    wres = lap.eliminate(wsys, lap.Schedule(policy="B2FT"))
    w_rank = len(wres.subs)
    w_nullity = nvars - w_rank
    if w_rank != expected_rank or w_nullity != expected_nullity:
        raise AssertionError(
            f"{name}: winnow mismatch: rank={w_rank}, nullity={w_nullity}; "
            f"expected rank={expected_rank}, nullity={expected_nullity}"
        )

    summary[name] = {
        "variables": nvars,
        "equations": len(rows),
        "ground_truth_center_or_commutant_dim": expected_nullity,
        "exact_Q_rank": rank_q,
        "rankscreen": {
            "verdict": verdict["verdict"],
            "rank": verdict["rank"],
            "k": verdict["k"],
            "agreement": verdict["agree"],
        },
        "winnow": {
            "prime": prime,
            "rank": w_rank,
            "nullity": w_nullity,
        },
        "status": "PASS",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootloops-root", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()

    root = Path(args.bootloops_root).resolve()
    tools = load_bootloops(root)

    # Finite-dimensional split benchmark.
    direct_basis = direct_sum_matrix_units(2, 3)
    direct_center_rows = commutant_equations(direct_basis, direct_basis)
    direct_commutant_rows = commutant_equations(matrix_units(5), direct_basis)

    # Group-algebra benchmark.
    s3_basis = s3_left_regular_basis()
    s3_center_rows = commutant_equations(s3_basis, s3_basis)
    s3_commutant_rows = commutant_equations(matrix_units(6), s3_basis)

    summary: dict = {
        "schema": "scg-hcws-toolchain-truth-benchmark-v1",
        "purpose": "pre-research capability QA",
        "semantic_status": "hypothesis-testing-only",
        "backend_scope": {
            "rankscreen": "finite linear-algebra elimination component",
            "winnow": "finite-field linear-algebra elimination component",
            "vopclose": "NOT-APPLICABLE to center/commutant; 1-D path-DE closure only",
        },
        "objects": {},
    }

    run_linear_backends(root, "M2_plus_M3_center", direct_center_rows, len(direct_basis), 2, summary["objects"])
    run_linear_backends(root, "M2_plus_M3_commutant", direct_commutant_rows, 25, 2, summary["objects"])
    run_linear_backends(root, "QS3_center", s3_center_rows, len(s3_basis), 3, summary["objects"])
    run_linear_backends(root, "QS3_commutant", s3_commutant_rows, 36, 6, summary["objects"])

    vop_guide = (tools / "vopclose" / "GUIDE.md").read_text(encoding="utf-8")
    if "1-D path-DE" not in vop_guide or "NOT-FOR" not in vop_guide:
        raise AssertionError("vopclose GUIDE no longer exposes its path-DE scope guard")
    summary["vopclose_scope_guard"] = "PASS"
    summary["overall"] = "PASS"

    payload = json.dumps(summary, indent=2, ensure_ascii=False)
    print(payload)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

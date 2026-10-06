#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
from collections import Counter
from pathlib import Path


CONFIRMED = "CONFIRMED"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("actual")
    ap.add_argument("expected")
    ap.add_argument(
        "--allow-provisional",
        action="store_true",
        help="compare a provisional baseline without failing solely because it is not yet CONFIRMED",
    )
    args = ap.parse_args()

    actual = json.loads(Path(args.actual).read_text(encoding="utf-8"))
    expected = json.loads(Path(args.expected).read_text(encoding="utf-8"))

    errors: list[str] = []
    promotion_pending = expected.get("status") != CONFIRMED
    if promotion_pending and not args.allow_provisional:
        errors.append(
            f"baseline status is {expected.get('status')!r}; "
            "only CONFIRMED baselines may gate acceptance"
        )

    want = expected["packages"]
    want_classes = expected.get("verification_class", {})
    got = {k: v.get("status", "UNKNOWN") for k, v in actual.items()}
    got_classes = {k: v.get("class", "unknown") for k, v in actual.items()}

    if set(got) != set(want):
        errors.append("package set mismatch")
    if set(got_classes) != set(want_classes):
        errors.append("verification-class package set mismatch")

    for name, status in want.items():
        if got.get(name) != status:
            errors.append(f"{name}: expected status={status!r} actual={got.get(name)!r}")

    for name, cls in want_classes.items():
        if got_classes.get(name) != cls:
            errors.append(
                f"{name}: expected verification_class={cls!r} actual={got_classes.get(name)!r}"
            )

    counts = Counter(got.values())
    expected_counts = Counter(expected["expected_counts"])
    if counts != expected_counts:
        errors.append(
            f"status count mismatch: expected={dict(expected_counts)!r} actual={dict(counts)!r}"
        )

    class_counts = Counter(got_classes.values())
    expected_class_counts = Counter(expected.get("expected_verification_class_counts", {}))
    if expected_class_counts and class_counts != expected_class_counts:
        errors.append(
            "verification-class count mismatch: "
            f"expected={dict(expected_class_counts)!r} actual={dict(class_counts)!r}"
        )

    out = {
        "schema": "scg-hcws-selftest-baseline-check-v2",
        "valid": not errors,
        "baseline_status": expected.get("status"),
        "promotion_pending": promotion_pending,
        "counts": dict(sorted(counts.items())),
        "verification_class_counts": dict(sorted(class_counts.items())),
        "errors": errors,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if errors:
        print("EXPECTED BASELINE CHECK: FAIL", file=sys.stderr)
        return 1
    if promotion_pending:
        print("EXPECTED BASELINE CHECK: PASS (comparison valid; promotion still pending)")
    else:
        print("EXPECTED BASELINE CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

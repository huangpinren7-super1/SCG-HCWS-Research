#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 3:
        print('usage: check_expected_selftests.py ACTUAL.json EXPECTED.json', file=sys.stderr)
        return 2
    actual=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    expected=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    want=expected['packages']
    got={k:v.get('status','UNKNOWN') for k,v in actual.items()}
    errors=[]
    if set(got)!=set(want):
        errors.append('package set mismatch')
    for name,status in want.items():
        if got.get(name)!=status:
            errors.append(f'{name}: expected={status!r} actual={got.get(name)!r}')
    counts={}
    for status in got.values(): counts[status]=counts.get(status,0)+1
    if counts != expected['expected_counts']:
        errors.append(f'count mismatch: expected={expected["expected_counts"]!r} actual={counts!r}')
    out={'schema':'scg-hcws-selftest-baseline-check-v1','valid':not errors,'counts':counts,'errors':errors}
    print(json.dumps(out,indent=2,ensure_ascii=False))
    if errors:
        print('EXPECTED BASELINE CHECK: FAIL',file=sys.stderr); return 1
    print('EXPECTED BASELINE CHECK: PASS'); return 0

if __name__=='__main__': raise SystemExit(main())

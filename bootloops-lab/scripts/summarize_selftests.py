#!/usr/bin/env python3
import json, pathlib, sys
p=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'selftest_results.json')
d=json.loads(p.read_text())
c={}
for r in d.values(): c[r.get('status','UNKNOWN')]=c.get(r.get('status','UNKNOWN'),0)+1
print('# BootLoops-Lab acceptance summary\n\n| Status | Count |\n|---|---:|')
for s,n in sorted(c.items()): print(f'| `{s}` | {n} |')
print('\n## Packages\n')
for k,r in sorted(d.items()): print(f'- `{k}`: **{r.get("status","UNKNOWN")}**')

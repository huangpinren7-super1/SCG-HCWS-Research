from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .catalog import load_catalog, read_guide
from .runner import run_acceptance


def main() -> int:
    ap = argparse.ArgumentParser(prog='bootloops-lab')
    ap.add_argument('--bootloops-root', default=os.environ.get('BOOTLOOPS_ROOT'))
    sub = ap.add_subparsers(dest='command', required=True)

    pcat = sub.add_parser('catalog')
    pcat.set_defaults(action='catalog')

    pguide = sub.add_parser('guide')
    pguide.add_argument('package')
    pguide.set_defaults(action='guide')

    pacc = sub.add_parser('acceptance')
    pacc.add_argument('package')
    pacc.add_argument('--timeout', type=int, default=300)
    pacc.set_defaults(action='acceptance')

    args = ap.parse_args()
    root = args.bootloops_root or Path('vendor/bootloops')
    if args.action == 'catalog':
        print(json.dumps(load_catalog(root), indent=2, ensure_ascii=False))
        return 0
    if args.action == 'guide':
        print(read_guide(root, args.package))
        return 0
    if args.action == 'acceptance':
        receipt = run_acceptance(args.package, root=str(root), timeout=args.timeout)
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return 0 if receipt['returncode'] == 0 else 1
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
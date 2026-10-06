from __future__ import annotations

import argparse
import json
import os

from .artifacts import list_artifacts, read_artifact
from .catalog import load_catalog, read_guide
from .profile import load_resident_profile, resident_packages
from .runner import resolve_bootloops_root, run_acceptance
from .verify import verify_job

def main() -> int:
    ap = argparse.ArgumentParser(prog="bootloops-lab")
    ap.add_argument("--bootloops-root", default=os.environ.get("BOOTLOOPS_ROOT"))
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog").set_defaults(action="catalog")
    sub.add_parser("resident").set_defaults(action="resident")

    guide = sub.add_parser("guide")
    guide.add_argument("package")
    guide.set_defaults(action="guide")

    run = sub.add_parser("run", aliases=["acceptance"])
    run.add_argument("package")
    run.add_argument("--timeout", type=int, default=300)
    run.set_defaults(action="run")

    verify = sub.add_parser("verify")
    verify.add_argument("job_id")
    verify.set_defaults(action="verify")

    artifacts = sub.add_parser("artifacts")
    artifacts.add_argument("job_id")
    artifacts.set_defaults(action="artifacts")

    artifact = sub.add_parser("artifact")
    artifact.add_argument("job_id")
    artifact.add_argument("name")
    artifact.set_defaults(action="artifact")

    args = ap.parse_args()
    root = resolve_bootloops_root(args.bootloops_root)

    if args.action == "catalog":
        print(json.dumps(load_catalog(root), indent=2, ensure_ascii=False))
        return 0
    if args.action == "resident":
        p = load_resident_profile()
        print(json.dumps({
            "schema": p["schema"],
            "bootloops_ref": p["bootloops_ref"],
            "resident_packages": resident_packages(p),
            "tiers": p["tiers"],
        }, indent=2, ensure_ascii=False))
        return 0
    if args.action == "guide":
        print(read_guide(root, args.package))
        return 0
    if args.action == "run":
        rec = run_acceptance(args.package, root=str(root), timeout=args.timeout)
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        return 0 if rec["status"] in ("PASS", "REFUSED (by design)") else 1
    if args.action == "verify":
        out = verify_job(root, args.job_id)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out["valid"] else 1
    if args.action == "artifacts":
        print(json.dumps(list_artifacts(root, args.job_id), indent=2, ensure_ascii=False))
        return 0
    if args.action == "artifact":
        print(json.dumps(read_artifact(root, args.job_id, args.name), indent=2, ensure_ascii=False))
        return 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bootloops_lab.artifacts import list_artifacts, read_artifact
from bootloops_lab.catalog import load_catalog, read_guide, resolve_root
from bootloops_lab.profile import load_resident_profile, resident_packages
from bootloops_lab.runner import run_acceptance
from bootloops_lab.verify import verify_job

REGISTRY = ROOT / "gateway" / "registry.yaml"

def registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}

def allowed(package: str) -> bool:
    return package in registry().get("tools", {})

def bootloops_root() -> Path:
    return resolve_root(os.environ.get("BOOTLOOPS_ROOT") or ROOT / "vendor" / "bootloops")

def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit("Install bootloops-lab/local/requirements-mcp.txt") from exc

    app = FastMCP("SCG-HCWS BootLoops Gateway")

    @app.tool()
    def health():
        "Return non-executing capability data."
        c = load_catalog(bootloops_root())
        r = registry()
        return {
            "schema": "scg-hcws-gateway-health-v1",
            "gateway_version": "0.2.0",
            "bootloops_ref": r["bootloops_ref"],
            "catalog_count": len(c),
            "allowlist_count": len(r["tools"]),
            "resident_count": len(resident_packages()),
            "python": platform.python_version(),
        }

    @app.tool()
    def catalog():
        "Return the allowlisted canonical package metadata."
        c = load_catalog(bootloops_root())
        r = registry()
        return {
            "schema": "scg-hcws-gateway-catalog-v1",
            "bootloops_ref": r["bootloops_ref"],
            "tools": {n: {**spec, **c[n]} for n, spec in r["tools"].items() if n in c},
        }

    @app.tool()
    def resident():
        "Return the resident local profile."
        p = load_resident_profile()
        return {
            "schema": p["schema"],
            "bootloops_ref": p["bootloops_ref"],
            "tiers": p["tiers"],
            "resident_packages": resident_packages(p),
        }

    @app.tool()
    def guide(package: str):
        "Return the exact upstream GUIDE.md for an allowlisted package."
        if not allowed(package):
            raise ValueError("package is not on Gateway allowlist: " + package)
        return read_guide(bootloops_root(), package)

    @app.tool()
    def run(package: str, timeout: int = 300):
        "Run one bounded canonical BootLoops battery."
        if not allowed(package):
            raise ValueError("package is not on Gateway allowlist: " + package)
        return run_acceptance(package, root=str(bootloops_root()), timeout=timeout)

    @app.tool()
    def verify(job_id: str):
        "Verify receipt and captured hashes; this is not a theorem proof."
        return verify_job(bootloops_root(), job_id)

    @app.tool()
    def artifacts(job_id: str):
        "List captured artifact metadata for one job."
        return {
            "schema": "scg-hcws-gateway-artifacts-v1",
            "job_id": job_id,
            "artifacts": list_artifacts(bootloops_root(), job_id),
        }

    @app.tool()
    def artifact(job_id: str, name: str):
        "Read one small text/JSON artifact from a job."
        return read_artifact(bootloops_root(), job_id, name)

    app.run()

if __name__ == "__main__":
    main()

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bootloops_lab.catalog import load_catalog, read_guide, resolve_root
from bootloops_lab.runner import run_acceptance

REGISTRY_PATH = ROOT / 'gateway' / 'registry.yaml'


def _load_registry():
    import yaml
    return yaml.safe_load(REGISTRY_PATH.read_text())


def _allowed(package: str) -> bool:
    return package in _load_registry()['tools']


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            'MCP dependency missing. Install bootloops-lab/local/requirements-mcp.txt first.'
        ) from exc

    app = FastMCP('SCG-HCWS BootLoops Gateway')

    @app.tool()
    def catalog() -> dict:
        'Return the allowlisted BootLoops tools and canonical metadata.'
        root = resolve_root(os.environ.get('BOOTLOOPS_ROOT') or ROOT / 'vendor' / 'bootloops')
        upstream = load_catalog(root)
        allow = _load_registry()['tools']
        return {
            'schema': 'scg-hcws-gateway-catalog-v1',
            'bootloops_ref': os.environ.get('BOOTLOOPS_REF', _load_registry()['bootloops_ref']),
            'tools': {
                name: {**allow_spec, **upstream[name]}
                for name, allow_spec in allow.items() if name in upstream
            },
        }

    @app.tool()
    def guide(package: str) -> str:
        'Return the upstream GUIDE.md for an allowlisted package.'
        if not _allowed(package):
            raise ValueError(f'Package is not on the Gateway allowlist: {package}')
        root = resolve_root(os.environ.get('BOOTLOOPS_ROOT') or ROOT / 'vendor' / 'bootloops')
        return read_guide(root, package)

    @app.tool()
    def run_acceptance_tool(package: str, timeout: int = 300) -> dict:
        'Run one canonical BootLoops acceptance battery and return its receipt.'
        if not _allowed(package):
            raise ValueError(f'Package is not on the Gateway allowlist: {package}')
        return run_acceptance(package, timeout=timeout)

    app.run()


if __name__ == '__main__':
    main()
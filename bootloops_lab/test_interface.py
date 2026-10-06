from pathlib import Path

from .catalog import load_catalog


def test_registry_contract_without_running_tools():
    root = Path(__file__).resolve().parents[1] / 'vendor' / 'bootloops'
    if not root.exists():
        return
    catalog = load_catalog(root)
    assert len(catalog) == 49
    for name, spec in catalog.items():
        assert name == spec['package']
        assert spec['command']
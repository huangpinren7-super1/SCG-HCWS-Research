from pathlib import Path

import yaml

from bootloops_lab.catalog import load_catalog


def test_gateway_registry_is_subset_of_canonical_catalog():
    root = Path(__file__).resolve().parents[1] / 'vendor' / 'bootloops'
    if not root.exists():
        return
    reg = yaml.safe_load((Path(__file__).parent / 'registry.yaml').read_text())
    catalog = load_catalog(root)
    assert reg['max_timeout'] == 1200
    assert reg['default_timeout'] == 300
    assert set(reg['tools']).issubset(catalog)


def test_no_shell_operation_in_registry():
    reg = yaml.safe_load((Path(__file__).parent / 'registry.yaml').read_text())
    for spec in reg['tools'].values():
        assert 'shell' not in spec
        assert 'command' not in spec
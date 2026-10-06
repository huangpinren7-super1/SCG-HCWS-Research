from pathlib import Path
import yaml
from bootloops_lab.catalog import load_catalog

def test_registry_contract():
    r = yaml.safe_load((Path(__file__).parent / "registry.yaml").read_text(encoding="utf-8"))
    assert r["default_timeout"] == 300
    assert r["max_timeout"] == 1200
    assert len(r["tools"]) >= 25
    root = Path(__file__).resolve().parents[1] / "vendor" / "bootloops"
    if root.exists():
        assert set(r["tools"]).issubset(load_catalog(root))

def test_registry_has_no_raw_execution_fields():
    r = yaml.safe_load((Path(__file__).parent / "registry.yaml").read_text(encoding="utf-8"))
    assert all("shell" not in spec and "command" not in spec for spec in r["tools"].values())

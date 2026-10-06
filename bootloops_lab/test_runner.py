from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import runner, verify
from .runner import run_acceptance
from .verify import verify_job


def fake(root: Path, writes: bool) -> Path:
    (root/"tools"/"fake").mkdir(parents=True)
    (root/"tools"/"README.md").write_text("| fake/ | fixture | selftest |\n", encoding="utf-8")
    (root/"tools"/"BATTERIES.json").write_text(
        json.dumps({"fake": {"cmd": "python3 tools/fake/test.py", "cwd": "root"}}),
        encoding="utf-8",
    )
    code = "import pathlib, json\n"
    if writes:
        code += "pathlib.Path('selftest_results.json').write_text(json.dumps({'fake':{'class':'selftest','status':'PASS'}}))\n"
    else:
        code += "print('no result')\n"
    (root/"tools"/"fake"/"test.py").write_text(code, encoding="utf-8")
    (root/"run_selftests.py").write_text(
        "import subprocess,sys\nsubprocess.run([sys.executable,'tools/fake/test.py'])\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "test"], cwd=root, check=True, capture_output=True)
    return root


def bind_test_registry(bl: Path, monkeypatch) -> None:
    ref = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=bl, text=True).strip()
    reg = bl/"registry.yaml"
    reg.write_text(f"bootloops_ref: {ref}\n", encoding="utf-8")
    monkeypatch.setattr(runner, "REGISTRY_PATH", reg)
    monkeypatch.setattr(verify, "REGISTRY_PATH", reg)


def test_receipt_verify(tmp_path, monkeypatch):
    bl = fake(tmp_path/"bl", True)
    bind_test_registry(bl, monkeypatch)
    monkeypatch.setenv("BOOTLOOPS_LAB_RUNS", str(tmp_path/"runs"))
    rec = run_acceptance("fake", root=str(bl), timeout=30)
    assert rec["status"] == "PASS"
    checked = verify_job(bl, rec["job_id"])
    assert checked["integrity_ok"]
    assert checked["acceptance_ok"]
    assert checked["valid"]


def test_no_stale_result(tmp_path, monkeypatch):
    bl = fake(tmp_path/"bl", False)
    bind_test_registry(bl, monkeypatch)
    (bl/"selftest_results.json").write_text(
        json.dumps({"fake": {"class": "selftest", "status": "PASS"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("BOOTLOOPS_LAB_RUNS", str(tmp_path/"runs"))
    rec = run_acceptance("fake", root=str(bl), timeout=30)
    assert rec["status"] == "UNKNOWN"

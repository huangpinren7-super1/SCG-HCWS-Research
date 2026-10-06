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
    reg = bl.parent/"registry.yaml"
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


def test_adversarial_receipt_semantics(tmp_path, monkeypatch):
    bl = fake(tmp_path/"bl", True)
    bind_test_registry(bl, monkeypatch)
    monkeypatch.setenv("BOOTLOOPS_LAB_RUNS", str(tmp_path/"runs"))
    rec = run_acceptance("fake", root=str(bl), timeout=30)
    job = tmp_path/"runs"/rec["job_id"]
    receipt = json.loads((job/"receipt.json").read_text(encoding="utf-8"))

    # Missing evidence must never verify as valid.
    missing = dict(receipt)
    missing.pop("stdout_sha256")
    missing_path = tmp_path/"missing.json"
    missing_path.write_text(json.dumps(missing), encoding="utf-8")
    missing_result = verify.verify_receipt(missing_path)
    assert not missing_result["integrity_ok"]
    assert not missing_result["acceptance_ok"]
    assert not missing_result["valid"]

    # A self-consistent FAIL is internally intact but is not an accepted run.
    result = json.loads((job/"selftest_results.json").read_text(encoding="utf-8"))
    result["fake"]["status"] = "FAIL"
    (job/"selftest_results.json").write_text(json.dumps(result), encoding="utf-8")
    failed = dict(receipt)
    failed["status"] = "FAIL"
    failed["result"] = result["fake"]
    from .receipt import sha256_file as _sha256_file
    failed["result_sha256"] = _sha256_file(job/"selftest_results.json")
    failed_path = tmp_path/"fail.json"
    failed_path.write_text(json.dumps(failed), encoding="utf-8")
    failed_result = verify.verify_receipt(failed_path)
    assert failed_result["integrity_ok"]
    assert not failed_result["acceptance_ok"]
    assert not failed_result["valid"]

def test_runner_refuses_registry_mismatch(tmp_path, monkeypatch):
    bl = fake(tmp_path/"bl", True)
    reg = bl/"registry.yaml"
    reg.write_text("bootloops_ref: " + "0"*40 + "\n", encoding="utf-8")
    monkeypatch.setattr(runner, "REGISTRY_PATH", reg)
    import pytest
    with pytest.raises(RuntimeError, match="BootLoops ref mismatch"):
        run_acceptance("fake", root=str(bl), timeout=30)

def test_runner_refuses_dirty_bootloops(tmp_path, monkeypatch):
    bl = fake(tmp_path/"bl", True)
    bind_test_registry(bl, monkeypatch)
    (bl/"DO_NOT_TOUCH").write_text("dirty\n", encoding="utf-8")
    import pytest
    with pytest.raises(RuntimeError, match="worktree is dirty"):
        run_acceptance("fake", root=str(bl), timeout=30)

from __future__ import annotations

import json
from pathlib import Path

from .runner import run_acceptance
from .verify import verify_job

def fake(root: Path, writes: bool) -> Path:
    (root/"tools"/"fake").mkdir(parents=True)
    (root/"tools"/"README.md").write_text("| fake/ | fixture | selftest |\n", encoding="utf-8")
    (root/"tools"/"BATTERIES.json").write_text(json.dumps({"fake":{"cmd":"python3 tools/fake/test.py","cwd":"root"}}), encoding="utf-8")
    code = "import pathlib, json\n"
    code += "pathlib.Path('selftest_results.json').write_text(json.dumps({'fake':{'status':'PASS'}}))\n" if writes else "print('no result')\n"
    (root/"tools"/"fake"/"test.py").write_text(code, encoding="utf-8")
    (root/"run_selftests.py").write_text("import subprocess,sys\nsubprocess.run([sys.executable,'tools/fake/test.py'])\n", encoding="utf-8")
    return root

def test_receipt_verify(tmp_path, monkeypatch):
    bl=fake(tmp_path/"bl",True)
    monkeypatch.setenv("BOOTLOOPS_LAB_RUNS",str(tmp_path/"runs"))
    rec=run_acceptance("fake",root=str(bl),timeout=30)
    assert rec["status"]=="PASS"
    assert verify_job(bl,rec["job_id"])["valid"]

def test_no_stale_result(tmp_path, monkeypatch):
    bl=fake(tmp_path/"bl",False)
    (bl/"selftest_results.json").write_text(json.dumps({"fake":{"status":"PASS"}}),encoding="utf-8")
    monkeypatch.setenv("BOOTLOOPS_LAB_RUNS",str(tmp_path/"runs"))
    rec=run_acceptance("fake",root=str(bl),timeout=30)
    assert rec["status"]=="UNKNOWN"

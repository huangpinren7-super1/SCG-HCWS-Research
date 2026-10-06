# BootLoops-Lab Local Resident Layer

This directory defines the local reusable scientific-computing layer for SCG-HCWS.

The goal is install-once, reuse-often, with a reproducible resident environment:
- keep the upstream BootLoops checkout untouched;
- keep the common Python exact/high-precision stack in one virtual environment;
- keep optional heavy engines explicit rather than silently substituted;
- expose a machine-readable catalog and per-run receipt;
- leave the GitHub Acceptance Battery as the canonical upstream verification.

Expected layout:
    SCG-HCWS-Research/
      bootloops-lab/local/
      vendor/bootloops/
      .venv/

Set BOOTLOOPS_ROOT when the checkout lives elsewhere. The resident Python layer is pinned in `requirements-core.txt`; bootstrap tooling is pinned in `requirements-tooling.txt`.

Bootstrap:
    bash bootloops-lab/local/bootstrap.sh

Then verify the environment strictly:
    bash bootloops-lab/local/doctor.sh

Then:
    python -m bootloops_lab.cli --bootloops-root vendor/bootloops catalog
    python -m bootloops_lab.cli --bootloops-root vendor/bootloops guide rankscreen
    python -m bootloops_lab.cli --bootloops-root vendor/bootloops acceptance rankscreen --timeout 300

The local interface never accepts arbitrary shell commands. It resolves commands from
BootLoops' canonical BATTERIES.json through the standardized runner.
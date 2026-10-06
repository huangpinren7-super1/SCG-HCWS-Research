# SCG-HCWS Computational Gateway

This is the thin local Gateway between SCG-HCWS research and BootLoops.

## API

- `health()` — reports the actual checkout SHA, registry SHA, worktree state, and runtime summary.
- `catalog()` — exposes the allowlisted canonical package metadata only when the actual checkout matches the registry pin.
- `guide(package)` — returns the upstream GUIDE for an allowlisted package.
- `run(package, timeout)` — executes one bounded canonical BootLoops battery.
- `verify(job_id)` — returns separate `integrity_ok` and `acceptance_ok` decisions.
- `artifacts(job_id)` / `artifact(job_id, name)` — inspect captured evidence.

## Security boundary

This Gateway is a **control plane, not a sandbox**. The package allowlist prevents arbitrary package selection and the runner accepts no raw shell command, but local callers can still execute code contained in the selected BootLoops checkout. `BOOTLOOPS_ROOT` is therefore a trusted-local operator setting, not a security boundary.

Every run refuses a dirty BootLoops worktree or a checkout whose actual `git rev-parse HEAD` does not equal the SHA pinned in `registry.yaml`. Receipts record runtime/dependency information and cryptographic hashes of captured outputs.

Those hashes protect against accidental drift and mismatched files; they do not prevent a malicious local operator from replacing the evidence and recomputing the hashes. Research-grade provenance needs an external anchor such as the Git commit, CI artifact digest, or a signature.

## Scope

The registry intentionally contains **33 allowlisted tools**, not all 49 BootLoops packages. The 49-package canonical battery remains the upstream acceptance surface; the Gateway is a narrower interactive control-plane subset. The omission is deliberate and should not be read as a failure to support the other packages.

Reference-sensitive inputs remain fail-closed. Missing CLINCH, Eichler, Galois, or Blade replay data are not synthesized.

## Optional MCP transport

```bash
python -m pip install -r bootloops-lab/local/requirements-mcp.txt
python gateway/server.py
```

Tool-specific mathematical adapters will be added only after their input/output contracts and independent truth benchmarks are frozen.

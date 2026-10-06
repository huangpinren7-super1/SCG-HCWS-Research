# SCG-HCWS Computational Gateway

This is the thin local Gateway between SCG-HCWS and BootLoops.

Initial API:
  catalog()
  guide(package)
  run_acceptance_tool(package, timeout)

The Gateway does not expose arbitrary shell commands. It resolves package commands
only through BootLoops' canonical BATTERIES.json and the upstream run_selftests.py.

Safety boundary:
1. package names are allowlisted in registry.yaml;
2. no raw shell command is accepted from the caller;
3. timeout is capped at 1200 seconds;
4. each run produces a machine-readable receipt with an output hash;
5. local concurrency is serialized because BootLoops writes a shared selftest_results.json;
6. missing reference data remains a named refusal rather than a fabricated fixture.

Optional MCP transport:
  python -m pip install -r bootloops-lab/local/requirements-mcp.txt
  python gateway/server.py

The initial Gateway is intentionally narrow. Tool-specific mathematical execution adapters
will be added only after their input/output contracts are frozen.
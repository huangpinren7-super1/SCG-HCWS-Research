# SCG-HCWS Research

Infrastructure-first scientific research repository for the frozen SCG/HCWS baseline.

## Foundations

- BootLoops source is checked out as an immutable external dependency at a full commit SHA.
- GitHub Actions runs the upstream 49-package acceptance battery on Ubuntu 24.04.
- Results retain the distinction between PASS, REFUSED (by design), and FAIL.
- The test JSON, source provenance, environment inventory, logs, and Markdown report are uploaded as a workflow artifact.

See bootloops-lab/README.md for the architecture and .github/workflows/bootloops.yml for the cloud runner.

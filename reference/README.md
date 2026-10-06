# Optional Reference/Data Banks

This directory is intentionally empty in the public baseline.

Several BootLoops packages have higher-tier tests that require externally supplied,
provenance-sensitive reference artifacts. We do not synthesize or invent these files.

Supported placements:
  reference/clinch/                 -> CLINCH_REFERENCE_DIR
  reference/eichler/true.json       -> G2KIT_TRUE_JSON
  reference/galois/                 -> GALOIS_CAMPAIGN_BANK
  reference/blade-port/             -> BLADE_PORT_ROOT

The cloud workflow exports an environment variable only when the corresponding real
payload exists. Otherwise BootLoops keeps its own fail-closed skip/refusal behavior.

Current baseline state:
- CLINCH reference bank: not supplied.
- Eichler genus-2 oracle: not supplied.
- Galois campaign/reference bank: not supplied.
- Blade port replay bank: not supplied.
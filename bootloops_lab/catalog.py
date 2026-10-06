from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def resolve_root(root: str | Path) -> Path:
    p = Path(root).expanduser().resolve()
    if not (p / 'run_selftests.py').is_file():
        raise FileNotFoundError(f'BootLoops root is not valid: {p}')
    return p


def load_catalog(root: str | Path) -> dict[str, dict[str, Any]]:
    root = resolve_root(root)
    manifest = json.loads((root / 'tools' / 'BATTERIES.json').read_text())
    classes: dict[str, str] = {}
    readme = (root / 'tools' / 'README.md').read_text()
    for line in readme.splitlines():
        m = re.match(r'\| \`([A-Za-z0-9_.-]+)/\` \|.*\| ([a-z-]+)', line)
        if m:
            classes[m.group(1)] = m.group(2)
    out: dict[str, dict[str, Any]] = {}
    for name, spec in sorted(manifest.items()):
        out[name] = {
            'package': name,
            'verification_class': classes.get(name, 'unknown'),
            'command': spec.get('cmd'),
            'cwd': spec.get('cwd', 'root'),
            'serial': bool(spec.get('serial')),
            'guide': str(root / 'tools' / name / 'GUIDE.md'),
            'has_project_toml': (root / 'tools' / name / 'Project.toml').is_file(),
        }
    return out


def read_guide(root: str | Path, package: str) -> str:
    root = resolve_root(root)
    path = root / 'tools' / package / 'GUIDE.md'
    if not path.is_file():
        raise KeyError(f'No GUIDE.md for package: {package}')
    return path.read_text()
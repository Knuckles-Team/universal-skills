#!/usr/bin/env python3
"""CE-021: Cross-repository XDG compliance check.

Scans a project's Python sources for hardcoded legacy home-directory paths
(e.g. ``~/.appname``) instead of the XDG base directories. The scan is local
and needs no knowledge-graph service.

CONCEPT:CE-021 — XDG Compliance Check
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox", "build", "dist"}
_ALLOWED_PREFIXES = ("~/.local", "~/.config", "~/.cache")
_TILDE_LITERAL = re.compile(r"""["'](~/[^"'\s]*)["']""")


def check_xdg_compliance(project_dir: str | None = None) -> dict[str, Any]:
    """Find string literals that point at non-XDG paths under ``~/``.

    Scans ``project_dir`` (default: the current directory).
    """
    root = Path(project_dir or ".").resolve()
    findings: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in _SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("Skipping unreadable file: %s", type(exc).__name__)
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for match in _TILDE_LITERAL.finditer(line):
                value = match.group(1)
                if not value.startswith(_ALLOWED_PREFIXES):
                    findings.append(
                        f"Found non-XDG path '{value}' in {path.relative_to(root)}:{number}"
                    )

    failed = bool(findings)
    return {
        "domain": "XDG Compliance",
        "score": 0 if failed else 100,
        "grade": "F" if failed else "A",
        "findings": findings,
        "justifications": [
            "Found hardcoded legacy home directory paths (~/.appname). Use XDG standard paths instead."
            if failed
            else "No non-XDG standard paths found in this scope."
        ],
    }


if __name__ == "__main__":
    import sys

    proj = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(check_xdg_compliance(proj), indent=2))

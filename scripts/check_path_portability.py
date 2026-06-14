#!/usr/bin/env python3
"""Cross-platform path portability gate (Windows / macOS / Linux).

Walks one or more roots and flags entries that break on a non-Linux filesystem:

* path length > ``--max-path`` (Windows MAX_PATH is 260)
* filename length > ``--max-name`` (255-byte component limit everywhere)
* Windows-illegal characters ``<>:"/\\|?*`` or control codes
* reserved DOS device names (CON/PRN/AUX/NUL/COM1-9/LPT1-9)
* trailing dot / space / ``~`` (silently dropped by Windows)
* case-insensitive collisions in a directory (break on macOS/Windows)

Exits non-zero when the violation count exceeds ``--max-violations`` — a ratchet
(like ``check_no_env_sprawl.py``) so the one-time normalization sweep can land
incrementally and the count only ever goes down. ``--json`` prints a machine
report. Mirror of ``universal_skills.skill_utilities`` rules; kept dependency-free.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

_WIN_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WIN_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "target",
    "dist",
    "build",
    ".tox",
    ".hypothesis",
    ".idea",
    ".eggs",
}


def scan(root: str, *, max_path: int, max_name: int) -> dict[str, list[str]]:
    """Return ``{violation_kind: [relpaths]}`` for everything under ``root``."""
    out: dict[str, list[str]] = {
        "long_path": [],
        "long_name": [],
        "illegal_char": [],
        "reserved_name": [],
        "trailing": [],
        "case_collision": [],
    }
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        lower_seen: dict[str, str] = {}
        for name in list(dirnames) + filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if len(rel) > max_path:
                out["long_path"].append(rel)
            if len(name) > max_name:
                out["long_name"].append(rel)
            if _WIN_ILLEGAL.search(name):
                out["illegal_char"].append(rel)
            if name.split(".")[0].upper() in _WIN_RESERVED:
                out["reserved_name"].append(rel)
            if name != name.rstrip(". ") or name.endswith("~"):
                out["trailing"].append(rel)
            low = name.lower()
            if low in lower_seen:
                out["case_collision"].append(rel)
            else:
                lower_seen[low] = name
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("roots", nargs="+", help="directories to scan")
    ap.add_argument("--max-path", type=int, default=200)
    ap.add_argument("--max-name", type=int, default=100)
    ap.add_argument(
        "--max-violations",
        type=int,
        default=0,
        help="ratchet ceiling; exit non-zero when total exceeds this",
    )
    ap.add_argument("--json", action="store_true", help="emit a JSON report")
    args = ap.parse_args(argv)

    totals: dict[str, list[str]] = {}
    for root in args.roots:
        rep = scan(root, max_path=args.max_path, max_name=args.max_name)
        for k, v in rep.items():
            totals.setdefault(k, []).extend(f"{root}::{p}" for p in v)

    count = sum(len(v) for v in totals.values())
    if args.json:
        print(
            json.dumps(
                {
                    "total": count,
                    "by_kind": {k: len(v) for k, v in totals.items()},
                    "violations": totals,
                },
                indent=2,
            )
        )
    else:
        for kind, items in totals.items():
            if items:
                print(f"{kind}: {len(items)}")
                for p in items[:10]:
                    print(f"  {p}")
                if len(items) > 10:
                    print(f"  … (+{len(items) - 10} more)")
        print(f"\nTOTAL violations: {count}  (ceiling: {args.max_violations})")

    if count > args.max_violations:
        print(
            f"\nFAIL: {count} portability violations exceed the ratchet "
            f"ceiling of {args.max_violations}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

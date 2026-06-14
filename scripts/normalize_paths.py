#!/usr/bin/env python3
"""One-time cross-platform path normalization sweep.

Walks a repo bottom-up and renames any file/dir whose name is not portable
(Windows/macOS/Linux) to a safe form via ``universal_skills.skill_utilities``:
length-bounded + illegal-char-stripped + reserved-name-guarded + case-deduped
within each directory. Idempotent and **dry-run by default** — pass ``--apply`` to
perform the renames. Pairs with ``check_path_portability.py`` (run it after to
confirm the count drops to the ratchet target).

Generated ``reference/`` doc trees can alternatively be *regenerated* through the
now-fixed crawler / skill-graph builder; prefer that where a clean source URL list
exists, since it also refreshes content. This sweep is for the in-tree files that
won't be regenerated (the handful of source-side reserved/trailing/case issues
first, then bulk generated trees).
"""

from __future__ import annotations

import argparse
import os
import sys

# Prefer the in-repo universal_skills (this checkout) over any stale installed copy
# so the shared portable-name rules match what the generators now emit.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from universal_skills.skill_utilities import (  # noqa: E402
    dedupe_caseless,
    portable_name,
)

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


def _plan_dir(
    dirpath: str, names: list[str], *, max_name: int
) -> list[tuple[str, str]]:
    """Return ``[(old, new)]`` renames for one directory (portable + case-deduped)."""
    portable = {n: portable_name(n, max_len=max_name) for n in names}
    deduped = dedupe_caseless(list(portable.values()))
    out: list[tuple[str, str]] = []
    for original in names:
        target = deduped.get(portable[original], portable[original])
        if target != original:
            out.append((original, target))
    return out


def sweep(root: str, *, apply: bool, max_name: int) -> list[tuple[str, str]]:
    """Compute (and optionally apply) renames under ``root`` (bottom-up)."""
    renames: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if any(part in _SKIP_DIRS for part in dirpath.split(os.sep)):
            continue
        for old, new in _plan_dir(
            dirpath, sorted(dirnames + filenames), max_name=max_name
        ):
            src = os.path.join(dirpath, old)
            dst = os.path.join(dirpath, new)
            renames.append((os.path.relpath(src, root), os.path.relpath(dst, root)))
            if apply:
                if os.path.exists(dst):
                    print(f"SKIP (target exists): {src} -> {dst}", file=sys.stderr)
                    continue
                os.rename(src, dst)
    return renames


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", help="repo directory to normalize")
    ap.add_argument(
        "--apply", action="store_true", help="perform renames (default: dry-run)"
    )
    ap.add_argument("--max-name", type=int, default=80)
    args = ap.parse_args(argv)

    renames = sweep(args.root, apply=args.apply, max_name=args.max_name)
    verb = "Renamed" if args.apply else "Would rename"
    for old, new in renames:
        print(f"{verb}: {old}  ->  {new}")
    print(
        f"\n{verb} {len(renames)} path(s)"
        + ("" if args.apply else " (dry-run; pass --apply)")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

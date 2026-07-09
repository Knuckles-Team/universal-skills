#!/usr/bin/env python3
"""Insert/normalize a ``skill_type`` frontmatter field on every SKILL.md under a root.

Taxonomy (CONCEPT: one field classifies every capability, path-independent):
  * ``skill``    — an atomic skill (one purpose, one trigger surface).
  * ``workflow`` — a dual-mode DAG grouping of atomic skills.
  * ``graph``    — a skill-graph (a captured reference manual / doc source).

Classification for ``--default skill`` roots: a SKILL.md is a ``workflow`` when its
path has a ``*-workflows`` domain segment or a ``/workflows/`` segment, OR its
frontmatter carries a swarm block (``team_config`` / ``specialist_ids`` /
``execution_mode``). Otherwise ``skill`` — a bare ``### Step`` section in an atomic
skill's docs does NOT make it a workflow (only a real swarm block or the workflow
directory taxonomy does). For ``--default graph`` (skill-graphs) every entry is ``graph``.

The field is inserted immediately after the ``name:`` line. Idempotent: an existing
``skill_type`` is overwritten only if it disagrees. Usage:
    python scripts/tag_skill_type.py --root <dir> --default {skill,graph}
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SWARM_RE = re.compile(r"^(team_config|specialist_ids|execution_mode):", re.MULTILINE)


def _classify(skill_md: Path, root: Path, default: str) -> str:
    if default == "graph":
        return "graph"
    rel = str(skill_md.parent.relative_to(root)).replace("\\", "/")
    segs = rel.split("/")
    if any(s.endswith("-workflows") for s in segs) or "workflows" in segs:
        return "workflow"
    text = skill_md.read_text(encoding="utf-8")
    fm = text.split("---", 2)[1] if text.startswith("---") else ""
    if SWARM_RE.search(fm):
        return "workflow"
    return "skill"


def _apply(skill_md: Path, skill_type: str) -> bool:
    """Ensure exactly one ``skill_type: <type>`` line in the frontmatter.

    Idempotent: pre-scans the frontmatter so a re-run replaces the existing field
    in place (never inserts a duplicate). Only inserts (after ``name:``) when absent.
    """
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    want = f"skill_type: {skill_type}"

    # Determine the frontmatter line range and whether the field already exists.
    fm_bounds = [i for i, ln in enumerate(lines) if ln.rstrip("\n") == "---"][:2]
    if len(fm_bounds) < 2:
        return False
    fm_lo, fm_hi = fm_bounds[0] + 1, fm_bounds[1]
    has_field = any(lines[i].startswith("skill_type:") for i in range(fm_lo, fm_hi))

    out: list[str] = []
    seen_field = False
    changed = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if fm_lo <= i < fm_hi and stripped.startswith("skill_type:"):
            if seen_field:  # collapse any accidental duplicates
                changed = True
                continue
            seen_field = True
            if stripped != want:
                out.append(want + ("\n" if line.endswith("\n") else ""))
                changed = True
            else:
                out.append(line)
            continue
        out.append(line)
        if not has_field and fm_lo <= i < fm_hi and stripped.startswith("name:"):
            out.append(f"skill_type: {skill_type}\n")
            changed = True
    if changed:
        skill_md.write_text("".join(out), encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--default", required=True, choices=["skill", "graph"])
    args = ap.parse_args()
    root = args.root.resolve()
    counts = {"skill": 0, "workflow": 0, "graph": 0}
    changed = 0
    for sk in sorted(root.rglob("SKILL.md")):
        st = _classify(sk, root, args.default)
        counts[st] += 1
        if _apply(sk, st):
            changed += 1
    print(f"{root}: {counts} (files changed: {changed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

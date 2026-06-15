#!/usr/bin/env python3
"""Atomicity Edict gate for universal-skills.

Enforces the governing rule (see AGENTS.md / STANDARDS.md):

  * Every skill is ATOMIC — one purpose, one capability. An atomic skill's
    SKILL.md must NOT be a workflow-in-disguise (no swarm orchestration block).
  * Every SKILL.md is Claude-compatible — a non-empty ``description`` of at most
    1024 chars (agents route on the description alone).
  * A skill-workflow (under ``universal_skills/workflows/``) is the dual-mode
    grouping of atomic skills: a ``depends_on`` DAG (machine layer) PLUS a
    rendered Claude-executable ``## Execution`` layer ending in the graph-os
    delegation footer.

Severity model so the gate is both meaningful and green:

  ERRORS (fail the gate, always):
    - A swarm-orchestration block (``team_config`` / ``specialist_ids`` /
      ``execution_mode``) inside an ATOMIC skill — that is a workflow, move it.
    - A missing ``description`` on any SKILL.md.
    - A ``description`` longer than 1024 characters.

  WARNINGS (reported; promoted to errors only with ``--strict``):
    - ``name`` frontmatter that does not equal the directory name.
    - An atomic skill that uses ``### Step N: ... [depends_on: ...]`` DAG syntax
      — a candidate workflow-in-disguise for human triage.
    - A workflow missing the dual-mode ``## Execution`` layer / delegation footer
      or whose DAG has a cycle.

Usage:
    python scripts/check_atomicity.py [--strict] [--root <universal_skills dir>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a dev dependency
    yaml = None

DESCRIPTION_MAX = 1024
SWARM_KEYS = ("team_config", "specialist_ids", "execution_mode")
DELEGATION_MARKER = "graph_orchestrate"  # appears in the standard delegation footer
STEP_DEP_RE = re.compile(
    r"^###\s+Step\s+\d+:.*\[depends_on:", re.MULTILINE
)
STEP_RE = re.compile(
    r"^###\s+Step\s+(\d+):\s*([a-zA-Z0-9_-]+)(?:\s*\[depends_on:\s*([^\]]+)\])?",
    re.MULTILINE,
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body). Empty frontmatter if absent."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return "", text


def _parse_frontmatter(fm_text: str) -> dict:
    if not fm_text.strip():
        return {}
    if yaml:
        try:
            return yaml.safe_load(fm_text) or {}
        except Exception:
            return {}
    fm: dict = {}
    for line in fm_text.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line.strip())
        if m:
            fm[m.group(1)] = m.group(2)
    return fm


def _has_dag_cycle(body: str) -> bool:
    steps = []
    for m in STEP_RE.finditer(body):
        deps = []
        if m.group(3):
            deps = [int(d) for d in re.findall(r"\d+", m.group(3))]
        steps.append((int(m.group(1)), deps))
    nums = {n for n, _ in steps}
    adj: dict[int, list[int]] = {n: [] for n in nums}
    for n, deps in steps:
        for d in deps:
            if d in nums:
                adj[d].append(n)
    state = {n: 0 for n in nums}

    def visit(u: int) -> bool:
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1 or (state[v] == 0 and visit(v)):
                return True
        state[u] = 2
        return False

    return any(state[u] == 0 and visit(u) for u in nums)


def find_skills_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "universal_skills"
        if cand.is_dir():
            return cand
    return Path.cwd() / "universal_skills"


def check(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    # Claude Code installs skills into a FLAT ~/.claude/skills/<name>/ tree, so a
    # directory name shared by two SKILL.md dirs (atomic skill vs workflow, or two
    # workflows) silently clobbers on install. Names must be globally unique.
    seen_names: dict[str, str] = {}

    for skill_md in sorted(root.rglob("SKILL.md")):
        rel = skill_md.relative_to(root.parent)
        # Skip bundled scaffolds/templates shipped inside a skill's assets.
        if "/assets/" in str(skill_md) or "skill_graphs" in str(skill_md):
            continue

        text = skill_md.read_text(encoding="utf-8", errors="replace")
        fm_text, body = _split_frontmatter(text)
        fm = _parse_frontmatter(fm_text)
        is_workflow = f"{root.name}/workflows/" in str(skill_md).replace("\\", "/")

        # --- Global name uniqueness (flatten-to-Claude collision) ---
        dir_name = skill_md.parent.name
        if dir_name in seen_names:
            warnings.append(
                f"{rel}: directory name `{dir_name}` collides with "
                f"{seen_names[dir_name]} (flattens to the same ~/.claude/skills/ entry)"
            )
        else:
            seen_names[dir_name] = str(rel)

        # --- Claude-compatibility (ERRORS) ---
        desc = fm.get("description")
        if not desc or not str(desc).strip():
            errors.append(f"{rel}: missing `description` frontmatter (Claude cannot route on it)")
        elif len(str(desc)) > DESCRIPTION_MAX:
            errors.append(
                f"{rel}: `description` is {len(str(desc))} chars (> {DESCRIPTION_MAX} max)"
            )

        # --- Atomicity (ERRORS for atomic skills) ---
        if not is_workflow:
            present = [k for k in SWARM_KEYS if re.search(rf"^{k}:", fm_text, re.MULTILINE)]
            if present:
                errors.append(
                    f"{rel}: atomic skill contains workflow/swarm block ({', '.join(present)}) "
                    f"— move it to universal_skills/workflows/<domain>/"
                )
            elif STEP_DEP_RE.search(body):
                warnings.append(
                    f"{rel}: atomic skill uses `### Step N [depends_on]` DAG syntax "
                    f"— candidate workflow-in-disguise (triage: split into atomic skills + a workflow)"
                )

        # --- name == directory ---
        name = fm.get("name")
        if name and name != skill_md.parent.name:
            warnings.append(
                f"{rel}: frontmatter name `{name}` != directory `{skill_md.parent.name}`"
            )

        # --- Workflow dual-mode (WARNINGS) ---
        if is_workflow:
            if not STEP_RE.search(body):
                warnings.append(f"{rel}: workflow has no `### Step N:` DAG (machine layer)")
            else:
                if _has_dag_cycle(body):
                    errors.append(f"{rel}: workflow DAG has a cycle")
                if "## Execution" not in body or DELEGATION_MARKER not in body:
                    warnings.append(
                        f"{rel}: workflow missing dual-mode Claude layer "
                        f"(`## Execution` section + graph-os delegation footer)"
                    )

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Atomicity Edict gate for universal-skills")
    ap.add_argument("--root", help="Path to the universal_skills package directory")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (candidates, dual-mode gaps, name!=dir) as errors",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else find_skills_root()
    if not root.is_dir():
        print(f"❌ universal_skills directory not found at {root}")
        return 2

    errors, warnings = check(root)

    if warnings:
        print(f"⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   - {w}")
    if errors:
        print(f"\n❌ {len(errors)} atomicity error(s):")
        for e in errors:
            print(f"   - {e}")

    if errors or (args.strict and warnings):
        print("\nAtomicity gate FAILED.")
        return 1
    print(f"\n✅ Atomicity gate passed ({len(warnings)} advisory warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

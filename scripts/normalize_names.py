#!/usr/bin/env python3
"""Normalize universal-skills skill directory + `name:` frontmatter to hyphens-only.

Every skill (atomic and workflow) must be kebab-case: the leaf directory name and
the `name:` frontmatter must contain no underscores and must match each other.

All underscore-bearing skill dirs today are workflows under ``*-workflows/``. A few
would, once hyphenated, collide with an existing atomic skill of the same name
(``code_enhancer`` -> ``code-enhancer`` clashes with ``core/code-enhancer``); those
workflow variants get a ``-workflow`` suffix so the flattened ``~/.claude/skills/``
namespace stays unique.

Idempotent: rerunning after a clean pass is a no-op. Uses ``git mv`` so history is
preserved. Prints the old->new rename map (also written to ``scripts/.rename_map.tsv``
for the reference-update step).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "universal_skills"
MAP_OUT = Path(__file__).resolve().parent / ".rename_map.tsv"


def _name_line_rewrite(skill_md: Path, new_name: str) -> None:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    in_fm = False
    fm_seen = 0
    done = False
    for line in lines:
        if line.rstrip("\n") == "---":
            fm_seen += 1
            in_fm = fm_seen == 1
            out.append(line)
            continue
        if in_fm and not done and line.startswith("name:"):
            nl = "\n" if line.endswith("\n") else ""
            out.append(f"name: {new_name}{nl}")
            done = True
            continue
        out.append(line)
    skill_md.write_text("".join(out), encoding="utf-8")


def main() -> int:
    skill_mds = sorted(ROOT.rglob("SKILL.md"))
    # Basenames that must stay reserved for atomic skills (no underscore already).
    atomic_names = {
        sk.parent.name
        for sk in skill_mds
        if "-workflows/" not in str(sk.parent.relative_to(ROOT)).replace("\\", "/")
    }

    renames: list[tuple[Path, Path, str, str]] = []
    for sk in skill_mds:
        d = sk.parent
        if "_" not in d.name:
            continue
        base = d.name.replace("_", "-")
        new_name = base
        if base in atomic_names:
            new_name = f"{base}-workflow"
        renames.append((d, d.parent / new_name, d.name, new_name))

    if not renames:
        print("No underscore skill dirs remain — nothing to normalize.")
        return 0

    map_lines = []
    for old_dir, new_dir, old_name, new_name in renames:
        if new_dir.exists():
            print(f"SKIP (target exists): {new_dir.relative_to(ROOT)}")
            continue
        subprocess.run(
            ["git", "mv", str(old_dir), str(new_dir)],
            cwd=ROOT.parent,
            check=True,
        )
        _name_line_rewrite(new_dir / "SKILL.md", new_name)
        rel_old = old_dir.relative_to(ROOT)
        rel_new = new_dir.relative_to(ROOT)
        print(f"{rel_old}  ->  {rel_new}   (name: {old_name} -> {new_name})")
        map_lines.append(f"{old_name}\t{new_name}\t{rel_old}\t{rel_new}")

    MAP_OUT.write_text("\n".join(map_lines) + "\n", encoding="utf-8")
    print(f"\n{len(map_lines)} dirs renamed. Map written to {MAP_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

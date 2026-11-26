#!/usr/bin/env python3
"""Compile each ``skill.spec.yml`` into ``SKILL.md``, test prompts and overlays (US-CONTENT-R009).

Usage:
    python scripts/compile_skill_spec.py            # write compiled files
    python scripts/compile_skill_spec.py --check    # exit 1 and name stale skills (hook)

The pure logic lives in ``universal_skills/skill_spec.py``. Exit codes: 0 clean,
1 stale or refused, 2 unreadable input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from universal_skills.skill_spec import (  # noqa: E402
    CompiledSkill,
    SkillSpec,
    SpecError,
    compile_skill,
    load_targets,
    parse_spec,
)

SKILLS = REPO / "universal_skills" / "skills"
OVERLAYS = REPO / "universal_skills" / "overlays"


def load_spec(path: Path, targets: dict | None = None) -> SkillSpec:
    return parse_spec(path.read_text(encoding="utf-8"), targets)


def planned_files(folder: Path, overlays_dir: Path, targets: dict | None) -> dict[Path, str]:
    """Map each output path to its compiled text. Raises ``SpecError`` and writes nothing."""
    spec = load_spec(folder / "skill.spec.yml", targets)
    skill_md = folder / "SKILL.md"
    compiled: CompiledSkill = compile_skill(spec, folder.name, skill_md.read_text(encoding="utf-8"))
    files = {skill_md: compiled.skill_md, folder / "evals" / "prompts.jsonl": compiled.prompts_jsonl}
    for name, text in compiled.overlays.items():
        files[overlays_dir / folder.name / name] = text
    return files


def run(skills: Path, overlays: Path, targets_path: Path | None, check: bool) -> int:
    targets = load_targets(targets_path)
    stale: list[str] = []
    status = 0
    for spec_file in sorted(skills.glob("*/skill.spec.yml")):
        folder = spec_file.parent
        try:
            files = planned_files(folder, overlays, targets)
        except SpecError as exc:
            print(f"{spec_file}: {exc.code}: {exc.detail}")
            status = 1
            continue
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{spec_file}: unreadable: {exc}")
            return 2
        for path, text in files.items():
            current = path.read_text(encoding="utf-8") if path.is_file() else None
            if current == text:
                continue
            if check:
                stale.append(folder.name)
                break
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    for name in sorted(set(stale)):
        print(f"SKILL_COMPILE_STALE: {name}")
    return 1 if stale or status else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="fail when a compiled file differs")
    ap.add_argument("--skills", type=Path, default=SKILLS)
    ap.add_argument("--overlays", type=Path, default=OVERLAYS)
    ap.add_argument("--targets", type=Path, default=None)
    args = ap.parse_args(argv)
    return run(args.skills, args.overlays, args.targets, args.check)


if __name__ == "__main__":
    sys.exit(main())

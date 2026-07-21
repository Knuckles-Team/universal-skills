#!/usr/bin/env python3
"""Validate and package one atomic universal skill as a .skill archive."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import zipfile
from pathlib import Path
from typing import Sequence

CONTRACT_PATH = Path(__file__).resolve().with_name("init_skill.py")
CONTRACT_SPEC = importlib.util.spec_from_file_location(
    "universal_skills_skill_contract", CONTRACT_PATH
)
if CONTRACT_SPEC is None or CONTRACT_SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not load skill contract from {CONTRACT_PATH}")
CONTRACT_MODULE = importlib.util.module_from_spec(CONTRACT_SPEC)
sys.modules.setdefault(CONTRACT_SPEC.name, CONTRACT_MODULE)
CONTRACT_SPEC.loader.exec_module(CONTRACT_MODULE)
validate_atomic_skill = CONTRACT_MODULE.validate_atomic_skill


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def package_skill(
    skill_path: str | Path, output_dir: str | Path | None = None
) -> Path | None:
    """Validate an atomic skill and write its archive atomically."""
    skill_path = Path(skill_path).resolve()
    errors = validate_atomic_skill(skill_path)
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return None

    output_path = Path(output_dir).resolve() if output_dir else Path.cwd().resolve()
    if _is_within(output_path, skill_path):
        print(
            "Error: output directory must be outside the skill folder",
            file=sys.stderr,
        )
        return None

    output_path.mkdir(parents=True, exist_ok=True)
    archive = output_path / f"{skill_path.name}.skill"
    temporary = output_path / f".{skill_path.name}.skill.tmp"

    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in sorted(skill_path.rglob("*")):
                if not file_path.is_file():
                    continue
                archive_name = Path(skill_path.name) / file_path.relative_to(skill_path)
                zip_file.write(file_path, archive_name)
        temporary.replace(archive)
    except (OSError, zipfile.BadZipFile) as exc:
        temporary.unlink(missing_ok=True)
        print(f"Error: failed to package skill: {type(exc).__name__}", file=sys.stderr)
        return None

    print(f"Packaged atomic skill: {archive}")
    return archive


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_path", help="Path to universal_skills/<domain>/<skill>")
    parser.add_argument("output_dir", nargs="?", help="Archive output directory")
    args = parser.parse_args(argv)
    return 0 if package_skill(args.skill_path, args.output_dir) else 1


if __name__ == "__main__":
    raise SystemExit(main())

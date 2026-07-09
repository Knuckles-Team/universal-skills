#!/usr/bin/env python3
"""Version parity for universal-skills: one ``metadata.version`` per SKILL.md, and a
``.bumpversion.cfg`` whose ``[bumpversion:file:...]`` stanzas cover every SKILL.md.

Two responsibilities (idempotent, safe to re-run):

1. Normalize versions — ensure each ``universal_skills/**/SKILL.md`` frontmatter has
   exactly one ``version: '<current_version>'`` line, nested under a ``metadata:``
   block (added if absent). bump2version's per-file search is a plain
   ``version: '{current_version}'`` match, so every file MUST carry the same current
   version string for the global bump to succeed.

2. Regenerate ``.bumpversion.cfg`` — keep the ``[bumpversion]`` header + the three
   base file stanzas (``pyproject.toml``, ``README.md``, ``skill_utilities.py``) and
   rewrite the SKILL.md stanza list from a live ``rglob`` so it never drifts from the
   tree again. Doubles as a coverage check (``--check`` exits non-zero on drift).

Usage:
    python scripts/gen_bumpversion.py            # apply
    python scripts/gen_bumpversion.py --check    # verify coverage only (CI)
"""

from __future__ import annotations

import argparse
import configparser
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO / "universal_skills"
CFG = REPO / ".bumpversion.cfg"

BASE_STANZAS = [
    ("pyproject.toml", 'version = "{current_version}"', 'version = "{new_version}"'),
    ("README.md", "Version: {current_version}", "Version: {new_version}"),
    (
        "universal_skills/skill_utilities.py",
        '__version__ = "{current_version}"',
        '__version__ = "{new_version}"',
    ),
]
VERSION_LINE = re.compile(r"^\s*version:\s*.+$")
METADATA_LINE = re.compile(r"^metadata:\s*$")


def _current_version() -> str:
    cp = configparser.ConfigParser()
    cp.read(CFG)
    return cp["bumpversion"]["current_version"].strip()


def _normalize_version(skill_md: Path, cur: str) -> bool:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    _, fm, body = text.split("---", 2)
    lines = fm.split("\n")

    # Drop every existing version: line (top-level or nested); we re-add one canonical.
    kept = [ln for ln in lines if not VERSION_LINE.match(ln)]

    want = f"version: '{cur}'"
    meta_idx = next((i for i, ln in enumerate(kept) if METADATA_LINE.match(ln)), None)
    if meta_idx is not None:
        # Indentation of the metadata block's children (default 2 spaces).
        indent = "  "
        for ln in kept[meta_idx + 1 :]:
            m = re.match(r"^(\s+)\S", ln)
            if m:
                indent = m.group(1)
                break
            if ln.strip() and not ln.startswith(" "):
                break
        kept.insert(meta_idx + 1, f"{indent}{want}")
    else:
        # Append a metadata block at the end of the frontmatter body.
        while kept and kept[-1].strip() == "":
            kept.pop()
        kept.append("metadata:")
        kept.append(f"  {want}")
        kept.append("")

    new_fm = "\n".join(kept)
    new_text = f"---{new_fm}---{body}"
    if new_text != text:
        skill_md.write_text(new_text, encoding="utf-8")
        return True
    return False


def _render_cfg(cur: str, skill_mds: list[Path]) -> str:
    out = [
        "[bumpversion]",
        f"current_version = {cur}",
        "commit = True",
        "tag = True",
        "",
    ]
    for rel, search, replace in BASE_STANZAS:
        out += [
            f"[bumpversion:file:{rel}]",
            f"search = {search}",
            f"replace = {replace}",
            "",
        ]
    for sk in skill_mds:
        rel = sk.relative_to(REPO).as_posix()
        out += [
            f"[bumpversion:file:{rel}]",
            "search = version: '{current_version}'",
            "replace = version: '{new_version}'",
            "",
        ]
    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 on drift")
    args = ap.parse_args()
    cur = _current_version()
    skill_mds = sorted(SKILLS_ROOT.rglob("SKILL.md"))

    if args.check:
        missing = [
            sk.relative_to(REPO).as_posix()
            for sk in skill_mds
            if f"version: '{cur}'" not in sk.read_text(encoding="utf-8")
        ]
        want_cfg = _render_cfg(cur, skill_mds)
        drift = want_cfg != (CFG.read_text(encoding="utf-8") if CFG.exists() else "")
        if missing:
            print(f"MISSING version '{cur}' in {len(missing)} SKILL.md:")
            for m in missing[:20]:
                print(f"  {m}")
        if drift:
            print(".bumpversion.cfg is stale vs the SKILL.md tree.")
        return 1 if (missing or drift) else 0

    changed = sum(_normalize_version(sk, cur) for sk in skill_mds)
    CFG.write_text(_render_cfg(cur, skill_mds), encoding="utf-8")
    print(
        f"Normalized version on {changed} SKILL.md; "
        f".bumpversion.cfg regenerated with {len(skill_mds) + len(BASE_STANZAS)} stanzas."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

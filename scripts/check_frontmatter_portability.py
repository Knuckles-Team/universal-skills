#!/usr/bin/env python3
"""Fleet-wide cross-agent SKILL.md frontmatter portability gate.

Simulates the CODEX per-agent frontmatter transform (``adapters.py``,
``AGENT_CONTRACTS["codex"]`` — the strictest target) against every ``SKILL.md``
under the given roots and asserts the transformed result is actually valid for
that target: only allowed top-level keys, a sane ``description``, a kebab-case
``name`` matching its directory, and (if present) a recognized ``skill_type``.

Also scans skill bodies/scripts for hardcoded agent skill-root paths
(``~/.config/devin/skills``, ``~/.codex/skills``, ``~/.claude/skills``) — a skill
should never hardcode where IT ITSELF (or another skill) gets installed; that is
the installer's job. ``install.py`` (both ``skill-installer`` and
``mcp-installer``, which legitimately define the per-tool path maps) is
allow-listed.

Ratchet CLI (mirrors ``check_path_portability.py``): positional ``roots``
(nargs="+"), ``--json``, ``--max-violations`` (default 0) — exits non-zero when
the violation count exceeds the ceiling, so a one-time sweep can land
incrementally and the count only ever goes down.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent
        / "universal_skills"
        / "core"
        / "skill-installer"
        / "scripts"
    ),
)
try:
    from adapters import AGENT_CONTRACTS, transform_frontmatter
except ImportError:  # pragma: no cover - adapters.py should always be importable here
    AGENT_CONTRACTS = {}
    transform_frontmatter = None

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a dev dependency
    yaml = None

_CONTRACT = AGENT_CONTRACTS.get("codex")
_SKILL_TYPES = ("skill", "workflow", "graph")
_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# A skill hardcoding where it (or any skill) installs to is the installer's job,
# not the skill's — flag it, except in the installers that legitimately own the
# per-tool path maps.
_HARDCODED_ROOT_RES = [
    re.compile(r"\.claude[/\\]skills"),
    re.compile(r"\.codex[/\\]skills"),
    re.compile(r"\.config[/\\]devin[/\\]skills"),
]
_ALLOWLISTED_SUFFIXES = (
    "skill-installer/scripts/install.py",
    "mcp-installer/scripts/install.py",
    # Explains the Codex contract's rationale in prose (not a hardcoded default).
    "skill-installer/scripts/adapters.py",
    # A cross-tool skill-DISCOVERY glob list (searches many tools' dirs to find
    # already-installed skills to grade) — not a hardcoded install default.
    "code-enhancer/scripts/grade_skills.py",
)
_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist"}


def _split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return "", text


def _check_skill_md(skill_md: Path, root: Path) -> list[str]:
    """Validate ``skill_md`` under the CODEX-transformed contract. Returns violation strings."""
    rel = skill_md.relative_to(root.parent) if root.parent in skill_md.parents else skill_md
    violations: list[str] = []
    if yaml is None or transform_frontmatter is None or _CONTRACT is None:
        return violations
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    transformed = transform_frontmatter(text, _CONTRACT)
    fm_text, _ = _split_frontmatter(transformed)
    if not fm_text.strip():
        violations.append(f"{rel}: no frontmatter block (Codex cannot read it)")
        return violations
    try:
        data = yaml.safe_load(fm_text) or {}
    except Exception as e:  # noqa: BLE001
        violations.append(f"{rel}: transformed frontmatter fails to parse: {e}")
        return violations
    if not isinstance(data, dict):
        violations.append(f"{rel}: transformed frontmatter is not a mapping")
        return violations

    extra = set(data.keys()) - _CONTRACT.allowed_top_level
    if extra:
        violations.append(
            f"{rel}: disallowed top-level key(s) survive the Codex transform: "
            f"{sorted(extra)}"
        )

    desc = data.get("description")
    if not desc or not str(desc).strip():
        violations.append(f"{rel}: missing/empty `description` after transform")
    else:
        desc_s = str(desc)
        if len(desc_s) > 1024:
            violations.append(f"{rel}: `description` is {len(desc_s)} chars (> 1024 max)")
        if "<" in desc_s or ">" in desc_s:
            violations.append(f"{rel}: `description` still contains `<`/`>` after sanitization")

    name = data.get("name")
    dir_name = skill_md.parent.name
    if not name:
        violations.append(f"{rel}: missing `name` after transform")
    elif name != dir_name:
        violations.append(f"{rel}: `name` ({name!r}) != directory ({dir_name!r})")
    elif not _KEBAB_RE.match(str(name)):
        violations.append(f"{rel}: `name` ({name!r}) is not kebab-case")

    orig_fm_text, _ = _split_frontmatter(text)
    try:
        orig_data = yaml.safe_load(orig_fm_text) or {}
    except Exception:  # noqa: BLE001
        orig_data = {}
    skill_type = orig_data.get("skill_type") if isinstance(orig_data, dict) else None
    if skill_type is not None and skill_type not in _SKILL_TYPES:
        violations.append(
            f"{rel}: `skill_type` ({skill_type!r}) not one of {_SKILL_TYPES}"
        )

    return violations


def _check_hardcoded_roots(path: Path, root: Path) -> list[str]:
    posix = path.as_posix()
    if any(posix.endswith(suffix) for suffix in _ALLOWLISTED_SUFFIXES):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rel = path.relative_to(root.parent) if root.parent in path.parents else path
    violations: list[str] = []
    for pattern in _HARDCODED_ROOT_RES:
        if pattern.search(text):
            violations.append(f"{rel}: hardcodes an agent skill-root path ({pattern.pattern})")
    return violations


def scan(root: str) -> dict[str, list[str]]:
    """Return ``{violation_kind: [violation strings]}`` for everything under ``root``."""
    out: dict[str, list[str]] = {"frontmatter": [], "hardcoded_root": []}
    root_path = Path(root)
    if not root_path.is_dir():
        return out
    for skill_md in sorted(root_path.rglob("SKILL.md")):
        if any(part in _SKIP_DIRS for part in skill_md.parts):
            continue
        out["frontmatter"].extend(_check_skill_md(skill_md, root_path))

    # Scoped to scripts, not docs: a doc legitimately DOCUMENTS these paths (e.g.
    # the skill-installer's own "Supported Tools" table); the real bug pattern is a
    # SCRIPT hardcoding its own install-root default instead of using SKILL_DIR.
    for path in sorted(root_path.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in (".py", ".sh"):
            continue
        out["hardcoded_root"].extend(_check_hardcoded_roots(path, root_path))

    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("roots", nargs="+", help="directories to scan for SKILL.md files")
    ap.add_argument("--json", action="store_true", help="emit a JSON report")
    ap.add_argument(
        "--max-violations",
        type=int,
        default=0,
        help="ratchet ceiling; exit non-zero when total exceeds this",
    )
    args = ap.parse_args(argv)

    totals: dict[str, list[str]] = {}
    for root in args.roots:
        rep = scan(root)
        for k, v in rep.items():
            totals.setdefault(k, []).extend(v)

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
                for item in items[:20]:
                    print(f"  {item}")
                if len(items) > 20:
                    print(f"  … (+{len(items) - 20} more)")
        print(f"\nTOTAL violations: {count}  (ceiling: {args.max_violations})")

    if count > args.max_violations:
        print(
            f"\nFAIL: {count} frontmatter-portability violations exceed the ratchet "
            f"ceiling of {args.max_violations}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

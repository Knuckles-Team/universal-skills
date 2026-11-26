#!/usr/bin/env python3
"""Skill stage budgets and frontmatter key placement (US-CONTENT-R011).

Stage 1 is the description (400 characters is about 100 tokens). Stage 2 is the
body (500 lines at most). Stage 3 is the files under ``references/``.

Output: one line per finding, ``<path>:<line>: <code>``.
Exit codes: 0 clean, 1 finding, 2 unreadable file.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_frontmatter_portability import _split_frontmatter  # noqa: E402
from check_skill_steps import Finding  # noqa: E402

DESCRIPTION_MAX = 400
BODY_MAX = 500
TIERS = ("domain", "core", "always-on")
METADATA_ONLY = ("tier", "owner_team", "personas", "load_script")
_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
_URL = re.compile(r"https?://|\bcurl\b|\bwget\b|\brequests\.|\burllib\b|\bhttpx\b")
_SERVER = re.compile(r"\"mcpServers\"|\bmcpServers\s*:|\bmcp_servers\b")
_SKIP = {"__pycache__", ".git", "node_modules"}


def _line_of(text: str, needle: str) -> int:
    for n, line in enumerate(text.split("\n"), 1):
        if needle in line:
            return n
    return 1


def lint_folder(folder: Path) -> list[Finding]:
    skill_md = folder / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    path = str(skill_md)
    findings: list[Finding] = []
    fm_text, body = _split_frontmatter(text)
    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    description = str(meta.get("description") or "")
    if len(description) > DESCRIPTION_MAX:
        findings.append(Finding(path, _line_of(text, "description"), "DESCRIPTION_TOO_LONG"))
    body_lines = body.strip("\n").split("\n")
    if len(body_lines) > BODY_MAX:
        findings.append(Finding(path, text.count("\n", 0, len(text) - len(body)) + BODY_MAX + 1, "BODY_TOO_LONG"))
    for n, line in enumerate(text.split("\n"), 1):
        for target in _LINK.findall(line):
            if "://" in target or target.startswith(("/", "mailto:")):
                continue
            rel = Path(os.path.normpath(Path(target)))
            linked = folder / rel
            if (
                linked.is_file()
                and rel.parts
                and rel.parts[0] not in ("references", "..")
                and rel.name != "SKILL.md"
                and linked.suffix in {".md", ".txt"}
            ):
                findings.append(Finding(path, n, "REFERENCE_NOT_STAGED"))
    for key in METADATA_ONLY:
        if key in meta:
            findings.append(Finding(path, _line_of(text, f"{key}:"), "KEY_NOT_IN_METADATA"))
    sub = meta.get("metadata") if isinstance(meta.get("metadata"), dict) else {}
    if "tier" in sub and sub["tier"] not in TIERS:
        findings.append(Finding(path, _line_of(text, "tier:"), "TIER_INVALID"))
    script = sub.get("load_script")
    if script is not None:
        target = folder / str(script)
        scripts_root = (folder / "scripts").resolve()
        if scripts_root not in target.resolve().parents or not target.is_file():
            findings.append(Finding(path, _line_of(text, "load_script"), "LOAD_SCRIPT_MISSING"))
        elif _URL.search(target.read_text(encoding="utf-8", errors="replace")):
            findings.append(Finding(path, _line_of(text, "load_script"), "LOAD_SCRIPT_NETWORK"))
    for file in sorted(folder.rglob("*")):
        if not file.is_file() or _SKIP & set(file.parts):
            continue
        if file.name == ".mcp.json":
            findings.append(Finding(str(file), 1, "SKILL_HAS_CONNECTOR_FILE"))
        elif file.stat().st_size < 1_000_000 and file.suffix in {".json", ".yml", ".yaml", ".toml", ".md"}:
            content = file.read_text(encoding="utf-8", errors="replace")
            if _SERVER.search(content):
                findings.append(Finding(str(file), _line_of(content, "mcp"), "SKILL_HAS_CONNECTOR_FILE"))
    return sorted(findings, key=lambda f: (f.path, f.line, f.code))


def _folders(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        if p.is_file():
            owner = next((a for a in p.parents if (a / "SKILL.md").is_file()), None)
            if owner and owner not in found:
                found.append(owner)
        elif p.is_dir():
            found += [p] if (p / "SKILL.md").is_file() else sorted(s.parent for s in p.glob("*/SKILL.md"))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path, help="SKILL.md files or skill folders")
    args = ap.parse_args(argv)
    status = 0
    for folder in _folders(args.paths):
        try:
            findings = lint_folder(folder)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{folder}: unreadable: {exc}", file=sys.stderr)
            return 2
        for finding in findings:
            print(finding)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())

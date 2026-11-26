#!/usr/bin/env python3
"""Skill step and error-recovery linter (US-CONTENT-R010).

Reads each ``SKILL.md``. The steps sit between ``<!-- spec:begin -->`` and
``<!-- spec:end -->`` or under the heading ``Steps``. Each step needs one
objective, one concrete command and one verification. A skill with steps needs a
table with the columns ``Failure``, ``Cause`` and ``Recovery``.

Output: one line per finding, ``<path>:<line>: <code>``.
Exit codes: 0 clean, 1 finding, 2 unreadable file.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_frontmatter_portability import _split_frontmatter  # noqa: E402

BEGIN = "<!-- spec:begin -->"
END = "<!-- spec:end -->"
_STEP = re.compile(r"^(\d+)\.\s+(.*)$")
_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
_MULTI = re.compile(r";\s|\band then\b|,\s*then\b|\bthen\b", re.I)
_COMMAND = re.compile(r"`[^`\n]+`")
_VERIFY = re.compile(r"\b(verify|verified|confirm|check|expect)\w*", re.I)
_VAGUE = re.compile(
    r"(please )?(just )?(try|retry|rerun|re-run|run)"
    r"( the step| the command| it| this)?( again| once more)?( later)?"
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    code: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code}"


def _steps_region(lines: list[str]) -> tuple[int, int] | None:
    """Return (first, last) 0-based line indexes of the steps region."""
    for i, line in enumerate(lines):
        if line.strip() == BEGIN:
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == END:
                    return i + 1, j
            return i + 1, len(lines)
    for i, line in enumerate(lines):
        m = _HEADING.match(line)
        if m and m.group(1).lower() == "steps":
            level = len(line) - len(line.lstrip("#"))
            end = len(lines)
            for j in range(i + 1, len(lines)):
                h = _HEADING.match(lines[j])
                if h and len(lines[j]) - len(lines[j].lstrip("#")) <= level:
                    end = j
                    break
            return i + 1, end
    return None


def _is_vague(cell: str) -> bool:
    text = cell.strip().lower().rstrip(".")
    return "`" not in text and bool(_VAGUE.fullmatch(text))


def _tables(lines: list[str]) -> list[tuple[int, list[str], list[list[str]]]]:
    """Return (line, header, rows) for each pipe table."""
    out = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip().lower() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            out.append((i + 1, header, rows))
            i = j
        else:
            i += 1
    return out


def lint_skill(text: str, path: str = "SKILL.md") -> list[Finding]:
    """Lint one SKILL.md text. Line numbers count from the first line of the file."""
    fm, body = _split_frontmatter(text)
    offset = text[: len(text) - len(body)].count("\n") if fm else 0
    lines = body.split("\n")
    findings: list[Finding] = []
    region = _steps_region(lines)
    steps: list[tuple[int, list[str]]] = []
    if region:
        first, last = region
        for k in range(first, last):
            m = _STEP.match(lines[k])
            if m:
                steps.append((k, [m.group(2)]))
            elif steps and lines[k].strip() and (lines[k].startswith((" ", "\t"))):
                steps[-1][1].append(lines[k].strip())
            elif steps and not lines[k].strip():
                continue
            elif steps and _HEADING.match(lines[k]):
                break
    if not steps:
        return [Finding(path, 1, "STEPS_MISSING")]
    for k, parts in steps:
        no = k + 1 + offset
        head = re.sub(r"`[^`]*`", "", parts[0])
        if _MULTI.search(head):
            findings.append(Finding(path, no, "STEP_MULTI_OBJECTIVE"))
        joined = " ".join(parts)
        if not _COMMAND.search(joined):
            findings.append(Finding(path, no, "STEP_NO_COMMAND"))
        if not _VERIFY.search(joined):
            findings.append(Finding(path, no, "STEP_NO_VERIFY"))
    recovery = [
        t for t in _tables(lines) if t[1][:3] == ["failure", "cause", "recovery"]
    ]
    if not recovery:
        findings.append(Finding(path, 1, "RECOVERY_TABLE_MISSING"))
    for line, _, rows in recovery:
        for n, row in enumerate(rows):
            if len(row) >= 3 and _is_vague(row[2]):
                findings.append(Finding(path, line + 2 + n + offset, "RECOVERY_VAGUE"))
    return sorted(findings, key=lambda f: (f.line, f.code))


def _targets(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        if p.is_dir():
            found += sorted(p.glob("SKILL.md")) or sorted(p.glob("*/SKILL.md"))
        elif p.name == "SKILL.md":
            found.append(p)
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path, help="SKILL.md files or skill folders")
    args = ap.parse_args(argv)
    status = 0
    for skill in _targets(args.paths):
        try:
            text = skill.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{skill}: unreadable: {exc}", file=sys.stderr)
            return 2
        for finding in lint_skill(text, str(skill)):
            print(finding)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())

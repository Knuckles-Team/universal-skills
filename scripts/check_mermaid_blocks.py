#!/usr/bin/env python3
"""Check that Mermaid Markdown fences are closed and contain a diagram."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


OPEN_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})\s*mermaid\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Problem:
    path: Path
    line: int
    message: str


def check_file(path: Path) -> list[Problem]:
    problems: list[Problem] = []
    opener_line = 0
    fence = ""
    content: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [Problem(path, 1, f"cannot read Markdown: {type(exc).__name__}")]

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not fence:
            match = OPEN_RE.fullmatch(stripped)
            if match:
                fence = match.group("fence")
                opener_line = line_number
                content = []
            continue
        if stripped == fence:
            if not any(item.strip() for item in content):
                problems.append(Problem(path, opener_line, "Mermaid block is empty"))
            fence = ""
            opener_line = 0
            content = []
        else:
            content.append(line)

    if fence:
        problems.append(Problem(path, opener_line, f"unclosed Mermaid `{fence}` fence"))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    problems = [problem for path in args.paths for problem in check_file(path)]
    for problem in problems:
        print(f"{problem.path}:{problem.line}: {problem.message}")
    if problems:
        print(f"Found {len(problems)} malformed Mermaid block(s).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

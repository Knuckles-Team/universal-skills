#!/usr/bin/env python3
"""Bring connector skill front matter inside the onboarding and budget rules.

A packaged ``SKILL.md`` fails the connector gate when its ``description`` is
longer than 400 characters (``DESCRIPTION_TOO_LONG``) and the engine refuses a
pack whose front matter holds ``& * ! { }`` (``MALFORMED_BODY``). This script
rewrites each skill so the description is a routing summary within the budget
and the full original text moves into the body, so no guidance is lost.

Usage: skill_budget_codemod.py <skills-dir> [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_DESCRIPTION = 400
UNSAFE = "&*!{}"
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def clean(text: str) -> str:
    """The text without any character the engine refuses in front matter."""
    text = re.sub(r"_\*", "_<op>", text).replace("&", "and")
    return " ".join("".join(c for c in text if c not in UNSAFE).split())


def fit_description(text: str, limit: int = MAX_DESCRIPTION) -> str:
    """A routing summary of ``text`` within ``limit`` characters.

    Keeps the first sentence and the ``Use ...`` trigger sentence, then every
    later sentence that still fits, in order.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    sentences = _SENTENCE.split(text)
    trigger = next((i for i, s in enumerate(sentences) if i and s.startswith("Use ")), None)
    chosen = {0}
    if trigger is not None and len(" ".join([sentences[0], sentences[trigger]])) <= limit:
        chosen.add(trigger)
    for index, sentence in enumerate(sentences):
        if index in chosen:
            continue
        candidate = sorted({*chosen, index})
        if len(" ".join(sentences[i] for i in candidate)) <= limit:
            chosen.add(index)
    result = " ".join(sentences[i] for i in sorted(chosen))
    if len(result) > limit:
        cut = result[: limit - 3].rsplit(" ", 1)[0].rstrip(",;:")
        result = cut + "..."
    return result


def _split(text: str) -> tuple[list[str], list[str]] | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1 :]
    return None


def _description_span(front: list[str]) -> tuple[int, int, str] | None:
    for i, line in enumerate(front):
        if line.startswith("description:"):
            j = i + 1
            while j < len(front) and front[j][:1].isspace():
                j += 1
            raw = " ".join([line[len("description:") :], *front[i + 1 : j]])
            value = raw.strip().lstrip(">|-+ ").strip()
            if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            return i, j, " ".join(value.split())
    return None


def rewrite(text: str) -> str:
    """The skill text with a budgeted description and the full text in the body."""
    parts = _split(text)
    if parts is None:
        return text
    front, body = parts
    span = _description_span(front)
    if span is None:
        return text
    start, end, original = span
    summary = fit_description(clean(original))
    new_front = [*front[:start], "description: >-", f"  {summary}", *front[end:]]
    if any(c in line for line in new_front for c in UNSAFE):
        new_front = [
            clean(line) if any(c in line for c in UNSAFE) else line for line in new_front
        ]
    full = clean(original)
    if summary != full and full not in " ".join(" ".join(body).split()):
        at = next((i for i, line in enumerate(body) if line.startswith("# ")), -1) + 1
        body = [*body[:at], "", f"Scope: {full}", *body[at:]]
    return "\n".join(["---", *new_front, "---", *body])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = 0
    for path in sorted(args.skills.glob("*/SKILL.md")):
        old = path.read_text(encoding="utf-8")
        new = rewrite(old)
        if new != old:
            changed += 1
            print(f"{'would change' if args.check else 'rewrote'} {path}")
            if not args.check:
                path.write_text(new, encoding="utf-8")
    return int(args.check and bool(changed))


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Minimalism / over-engineering audit for the code-enhancer skill.

A deterministic, LLM-free pass that hunts the debt an unconstrained agent leaves
behind: hand-rolled stdlib, commented-out code, and trivial wrapper functions —
the "lazy senior dev" lens (the best code is the code never written). Findings use
the ponytail tag taxonomy and end with a ``net: -N lines possible`` estimate.

It also reports how many intentional shortcuts already carry a ``ponytail:`` /
``upgrade-path:`` marker — the convention of naming a shortcut's ceiling and
migration route *in the code* (see references/minimalism-ladder.md), so reviewers
can tell a deliberate simplification from an accidental one.

Tags (ponytail): ``delete:`` (dead/commented code), ``stdlib:`` (reinvented
stdlib), ``yagni:`` (single-use abstraction), ``shrink:`` (same logic, fewer lines).

CONCEPT:CE-040 — Minimalism & over-engineering audit

Usage:
    python analyze_minimalism.py <repo_path>
    python analyze_minimalism.py --self-test
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

_SKIP_PARTS = {
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".git",
    "target",
    "build",
    "dist",
    ".mypy_cache",
    ".ruff_cache",
}

# A commented line that looks like *code*, not prose (used to find leftover blocks).
_COMMENTED_CODE = re.compile(
    r"^\s*#\s*("
    r"def |class |return |import |from \w|if |elif |else:|for |while |try:|except|with |print\(|"
    r"[A-Za-z_][\w.]*\s*=[^=]|[A-Za-z_][\w.]*\("
    r")"
)
# "same logic, fewer lines" smells, matched on real (non-comment) code lines.
_SHRINK_PATTERNS = [
    (re.compile(r"==\s*True\b"), "compare `== True`", "drop it: `if x:`"),
    (re.compile(r"==\s*False\b"), "compare `== False`", "use `not x`"),
    (re.compile(r"[!=]=\s*None\b"), "compare to None with `==`", "use `is`/`is not`"),
    (
        re.compile(r"\blen\([^()]*\)\s*[=!]=\s*0\b"),
        "`len(x) == 0`",
        "use `not x` / `if x`",
    ),
]


def _py_files(root: Path) -> list[Path]:
    return [
        f
        for f in root.rglob("*.py")
        if not _SKIP_PARTS.intersection(f.parts) and not f.name.startswith("test_")
    ]


def _scan_lines(rel: str, source: str) -> tuple[list[str], int]:
    """Line-based detectors: commented-code blocks + shrink smells. Returns
    (findings, deletable_line_estimate)."""
    findings: list[str] = []
    deletable = 0
    lines = source.splitlines()

    # Commented-out code: report runs of >= 2 consecutive code-like comment lines.
    run_start = 0
    run_len = 0
    for i, line in enumerate(lines, 1):
        if _COMMENTED_CODE.match(line):
            if run_len == 0:
                run_start = i
            run_len += 1
        else:
            if run_len >= 2:
                findings.append(
                    f"delete: {run_len} lines of commented-out code. "
                    f"remove it (git remembers). [{rel}:{run_start}]"
                )
                deletable += run_len
            run_len = 0
    if run_len >= 2:
        findings.append(
            f"delete: {run_len} lines of commented-out code. "
            f"remove it (git remembers). [{rel}:{run_start}]"
        )
        deletable += run_len

    # Shrink smells (skip comment lines so we don't flag the detector's own examples).
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue
        for pat, what, repl in _SHRINK_PATTERNS:
            if pat.search(line):
                findings.append(f"shrink: {what}. {repl}. [{rel}:{i}]")
                deletable += 1
                break
    return findings, deletable


def _scan_ast(rel: str, source: str) -> list[str]:
    """AST detectors: trivial wrapper functions (single `return call(...)` body)."""
    findings: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("__"):
            continue
        body = [
            s
            for s in node.body
            if not isinstance(s, ast.Expr)
            or not isinstance(getattr(s, "value", None), ast.Constant)
        ]  # drop docstring
        if len(body) == 1 and isinstance(body[0], ast.Return):
            val = body[0].value
            if isinstance(val, ast.Call) and not node.decorator_list:
                findings.append(
                    f"yagni: `{node.name}()` only forwards to another call. "
                    f"inline it or drop the wrapper. [{rel}:{node.lineno}]"
                )
    return findings


def analyze_minimalism(root_dir: str = ".") -> dict:
    root = Path(root_dir).resolve()
    files = _py_files(root)
    if not files:
        return {
            "domain": "Minimalism Audit",
            "score": 100,
            "grade": "A",
            "findings": ["No Python files to audit"],
            "justifications": [],
            "minimalism": {"net_lines": 0, "marked_shortcuts": 0},
        }

    all_findings: list[str] = []
    deletable_total = 0
    marked = 0
    for f in files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(f.relative_to(root))
        marked += len(re.findall(r"\b(ponytail|upgrade-path)\s*:", source))
        line_findings, deletable = _scan_lines(rel, source)
        all_findings.extend(line_findings)
        all_findings.extend(_scan_ast(rel, source))
        deletable_total += deletable

    # Ranked: delete (biggest cut) first, then yagni, then shrink.
    rank = {"delete:": 0, "stdlib:": 1, "yagni:": 2, "shrink:": 3}
    all_findings.sort(key=lambda s: rank.get(s.split(" ", 1)[0], 9))

    score = max(0, 100 - min(60, len(all_findings) * 2))
    summary = (
        f"net: -{deletable_total} lines possible across {len(files)} files "
        f"({len(all_findings)} minimalism findings; {marked} marked shortcuts)"
        if all_findings
        else "Lean already. Ship."
    )
    grade = (
        "A"
        if score >= 90
        else "B"
        if score >= 80
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )
    return {
        "domain": "Minimalism Audit",
        "score": score,
        "grade": grade,
        "findings": [summary, *all_findings[:24]],
        "justifications": [
            {
                "criterion": "minimalism",
                "points": score,
                "evidence": f"findings={len(all_findings)} deletable_lines={deletable_total} "
                f"marked_shortcuts={marked}",
                "reasoning": "Deterministic audit for commented code, reinvented stdlib, "
                "trivial wrappers, and shrinkable expressions (ponytail lazy-first lens).",
            }
        ],
        "minimalism": {
            "net_lines": deletable_total,
            "marked_shortcuts": marked,
            "items": all_findings[:50],
        },
    }


def _self_test() -> int:
    import tempfile

    sample = (
        "# def old_thing():\n"
        "#     return 1\n"
        "#     x = compute()\n"
        "def is_ready(flag):\n"
        "    if flag == True:\n"
        "        return helper(flag)\n"
        "\n"
        "def wrap(a, b):\n"
        "    return other(a, b)  # ponytail: thin shim, inline if it stays trivial\n"
    )
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "m.py").write_text(sample)
        res = analyze_minimalism(td)
    joined = " ".join(res["findings"])
    assert "delete:" in joined, joined
    assert "shrink:" in joined, joined
    assert "yagni:" in joined, joined
    assert res["minimalism"]["marked_shortcuts"] == 1, res["minimalism"]
    assert res["score"] < 100
    print("analyze_minimalism self-test: OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(_self_test())
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_minimalism(target), indent=2))

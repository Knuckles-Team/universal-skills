#!/usr/bin/env python3
"""CA-004: Code quality — complexity, duplication, stubs, function length.

Usage: python analyze_code_quality.py /path/to/project

CONCEPT:CA-004 — Code Quality & Maintainability
"""

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
}
STUB_PATTERNS = [
    re.compile(r"\bpass\b\s*$"),
    re.compile(r"raise\s+NotImplementedError"),
    re.compile(r"#\s*(TODO|FIXME|HACK|XXX|STUB)", re.IGNORECASE),
    re.compile(r"\.\.\.\s*$"),
]


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity per function."""

    def __init__(self):
        self.functions = []

    def _complexity(self, node):
        """Count decision points."""
        c = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                c += 1
            elif isinstance(child, ast.BoolOp):
                c += len(child.values) - 1
            elif isinstance(child, ast.Assert):
                c += 1
        return c

    def visit_FunctionDef(self, node):
        self.functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "complexity": self._complexity(node),
                "length": (node.end_lineno or node.lineno) - node.lineno + 1,
            }
        )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_python_quality(project_path: Path) -> dict:
    """Analyze Python code quality metrics."""
    all_functions = []
    total_loc = 0
    stub_count = 0
    todo_count = 0
    file_count = 0

    for pyfile in project_path.rglob("*.py"):
        rel = pyfile.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        if "test" in str(rel).lower():
            continue  # Skip test files for quality metrics

        file_count += 1
        try:
            content = pyfile.read_text(errors="ignore")
            lines = content.split("\n")
            total_loc += len(lines)

            for line in lines:
                for pat in STUB_PATTERNS:
                    if pat.search(line):
                        if "TODO" in line.upper() or "FIXME" in line.upper():
                            todo_count += 1
                        else:
                            stub_count += 1
                        break

            tree = ast.parse(content)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            for func in visitor.functions:
                func["file"] = str(rel)
            all_functions.extend(visitor.functions)
        except (SyntaxError, UnicodeDecodeError):
            pass

    complexities = [f["complexity"] for f in all_functions] if all_functions else [0]
    lengths = [f["length"] for f in all_functions] if all_functions else [0]

    return {
        "file_count": file_count,
        "total_loc": total_loc,
        "function_count": len(all_functions),
        "complexity": {
            "avg": round(sum(complexities) / max(len(complexities), 1), 2),
            "max": max(complexities),
            "high_complexity": len([c for c in complexities if c > 10]),
        },
        "function_length": {
            "avg": round(sum(lengths) / max(len(lengths), 1), 1),
            "max": max(lengths),
            "long_functions": len([l for l in lengths if l > 50]),
        },
        "stubs": {"stub_count": stub_count, "todo_count": todo_count},
        "top_complex": sorted(all_functions, key=lambda x: -x["complexity"])[:5],
        "top_long": sorted(all_functions, key=lambda x: -x["length"])[:5],
    }


def detect_duplication(project_path: Path) -> dict:
    """Basic line-level duplication detection via fingerprinting."""
    line_hashes: Counter = Counter()
    total_lines = 0

    for pyfile in project_path.rglob("*.py"):
        rel = pyfile.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            for line in pyfile.read_text(errors="ignore").split("\n"):
                stripped = line.strip()
                if len(stripped) > 20 and not stripped.startswith("#"):
                    line_hashes[stripped] += 1
                    total_lines += 1
        except (OSError, UnicodeDecodeError):
            pass

    duplicated = sum(count - 1 for count in line_hashes.values() if count > 1)
    return {
        "total_significant_lines": total_lines,
        "duplicated_lines": duplicated,
        "duplication_pct": round(duplicated / max(total_lines, 1) * 100, 1),
    }


def score_code_quality(quality: dict, duplication: dict) -> dict:
    """Calculate 0-100 code quality score."""
    score = 100
    details = []

    # Complexity penalties
    avg_cx = quality.get("complexity", {}).get("avg", 0)
    if avg_cx > 15:
        score -= 25
        details.append(f"Very high avg complexity ({avg_cx}): -25")
    elif avg_cx > 10:
        score -= 15
        details.append(f"High avg complexity ({avg_cx}): -15")
    elif avg_cx > 7:
        score -= 5
        details.append(f"Moderate complexity ({avg_cx}): -5")
    else:
        details.append(f"Good complexity ({avg_cx}): no penalty")

    # Function length penalties
    long = quality.get("function_length", {}).get("long_functions", 0)
    if long > 10:
        score -= 15
        details.append(f"Many long functions ({long}): -15")
    elif long > 5:
        score -= 10
        details.append(f"Some long functions ({long}): -10")

    # Stub/TODO penalties
    stubs = quality.get("stubs", {}).get("stub_count", 0)
    todos = quality.get("stubs", {}).get("todo_count", 0)
    if stubs > 20:
        score -= 20
        details.append(f"Many stubs ({stubs}): -20")
    elif stubs > 5:
        score -= 10
        details.append(f"Some stubs ({stubs}): -10")
    if todos > 20:
        score -= 5
        details.append(f"Many TODOs ({todos}): -5")

    # Duplication penalties
    dup_pct = duplication.get("duplication_pct", 0)
    if dup_pct > 20:
        score -= 20
        details.append(f"High duplication ({dup_pct}%): -20")
    elif dup_pct > 10:
        score -= 10
        details.append(f"Moderate duplication ({dup_pct}%): -10")
    elif dup_pct > 5:
        score -= 5
        details.append(f"Low duplication ({dup_pct}%): -5")

    score = max(score, 0)
    grade = (
        "A+"
        if score >= 95
        else "A"
        if score >= 90
        else "B+"
        if score >= 85
        else "B"
        if score >= 80
        else "C+"
        if score >= 75
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )
    return {"score": score, "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_code_quality.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    quality = analyze_python_quality(project_path)
    duplication = detect_duplication(project_path)
    scoring = score_code_quality(quality, duplication)

    print(
        json.dumps(
            {
                "domain": "CA-004",
                "domain_name": "Code Quality",
                "project": str(project_path),
                "quality_metrics": quality,
                "duplication": duplication,
                "scoring": scoring,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

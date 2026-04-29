#!/usr/bin/env python3
"""FR-003: Codebase optimization analysis for code-enhancer skill.

Uses the ast module to measure cyclomatic complexity, function length,
nesting depth, duplication, and module coupling.

CONCEPT:CE-003 — Codebase Quality Analysis
"""

import ast
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


def _cyclomatic_complexity(node: ast.AST) -> int:
    """Compute McCabe cyclomatic complexity for a function/method node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, (ast.Assert, ast.comprehension)):
            complexity += 1
    return complexity


def _max_nesting_depth(node: ast.AST, current: int = 0) -> int:
    """Compute maximum nesting depth within a function."""
    nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)
    max_depth = current
    for child in ast.iter_child_nodes(node):
        if isinstance(child, nesting_nodes):
            max_depth = max(max_depth, _max_nesting_depth(child, current + 1))
        else:
            max_depth = max(max_depth, _max_nesting_depth(child, current))
    return max_depth


def _analyze_file(filepath: Path) -> dict:
    """Analyze a single Python file for quality metrics."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return {"error": f"Cannot parse {filepath}"}

    lines = source.splitlines()
    functions: list[dict] = []
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno + 1)
            length = end_line - node.lineno + 1
            cc = _cyclomatic_complexity(node)
            depth = _max_nesting_depth(node)
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "length": length,
                "complexity": cc,
                "nesting_depth": depth,
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])

    # Normalize source for duplication hashing (strip whitespace/comments)
    normalized_blocks: list[str] = []
    block: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            block.append(stripped)
        else:
            if len(block) >= 4:
                normalized_blocks.append("\n".join(block))
            block = []
    if len(block) >= 4:
        normalized_blocks.append("\n".join(block))

    block_hashes = [hashlib.md5(b.encode()).hexdigest() for b in normalized_blocks]

    return {
        "file": str(filepath),
        "total_lines": len(lines),
        "functions": functions,
        "imports": list(set(imports)),
        "block_hashes": block_hashes,
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def analyze_codebase(root_dir: str = ".") -> dict:
    """Analyze codebase quality and produce scored results."""
    root = Path(root_dir).resolve()
    py_files = [f for f in root.rglob("*.py")
                if ".venv" not in f.parts and "__pycache__" not in f.parts
                and "node_modules" not in f.parts and ".git" not in f.parts]

    if not py_files:
        return {"domain": "Codebase Optimization", "score": 0, "grade": "F",
                "findings": ["No Python files found"], "justifications": [], "metrics": {}}

    all_functions: list[dict] = []
    all_hashes: list[str] = []
    import_graph: dict[str, list[str]] = {}
    total_lines = 0
    file_count = len(py_files)
    parse_errors = 0

    for f in py_files:
        result = _analyze_file(f)
        if "error" in result:
            parse_errors += 1
            continue
        total_lines += result["total_lines"]
        for func in result["functions"]:
            func["file"] = result["file"]
            all_functions.append(func)
        all_hashes.extend(result["block_hashes"])
        import_graph[result["file"]] = result["imports"]

    # Compute metrics
    complexities = [f["complexity"] for f in all_functions] or [0]
    lengths = [f["length"] for f in all_functions] or [0]
    depths = [f["nesting_depth"] for f in all_functions] or [0]

    avg_complexity = sum(complexities) / len(complexities)
    max_complexity = max(complexities)
    avg_length = sum(lengths) / len(lengths)
    max_length = max(lengths)
    max_depth = max(depths)

    # Duplication: count hash collisions
    hash_counts = defaultdict(int)
    for h in all_hashes:
        hash_counts[h] += 1
    duplicate_blocks = sum(1 for c in hash_counts.values() if c > 1)
    duplication_ratio = duplicate_blocks / max(len(all_hashes), 1)

    # Long functions (>50 lines)
    long_functions = [f for f in all_functions if f["length"] > 50]
    # Complex functions (CC > 10)
    complex_functions = [f for f in all_functions if f["complexity"] > 10]
    # Deep nesting (>4)
    deep_functions = [f for f in all_functions if f["nesting_depth"] > 4]

    # Monolithic files (>1000 lines) — should be split into directories or logical modules
    file_sizes: dict[str, int] = {}
    for f in py_files:
        try:
            line_count = len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
            file_sizes[str(f)] = line_count
        except Exception:
            pass
    monolithic_files = [(path, lc) for path, lc in file_sizes.items() if lc > 1000]
    monolithic_files.sort(key=lambda x: x[1], reverse=True)

    # Scoring (start at 100, deduct)
    score = 100
    findings: list[str] = []

    # Complexity penalty
    if avg_complexity > 10:
        score -= 15
        findings.append(f"High avg cyclomatic complexity: {avg_complexity:.1f}")
    elif avg_complexity > 7:
        score -= 8
        findings.append(f"Moderate avg cyclomatic complexity: {avg_complexity:.1f}")
    elif avg_complexity > 5:
        score -= 3

    # Long function penalty
    if len(long_functions) > 10:
        score -= 15
        findings.append(f"{len(long_functions)} functions exceed 50 lines")
    elif len(long_functions) > 5:
        score -= 8
    elif len(long_functions) > 0:
        score -= 3

    # Monolithic file penalty (>1000 lines)
    if len(monolithic_files) > 3:
        score -= 15
        findings.append(
            f"{len(monolithic_files)} monolithic files (>1000 lines) — "
            "consider splitting into packages or logical modules"
        )
    elif len(monolithic_files) > 1:
        score -= 8
        findings.append(
            f"{len(monolithic_files)} monolithic files (>1000 lines): "
            + ", ".join(Path(p).name + f" ({lc}L)" for p, lc in monolithic_files[:5])
        )
    elif len(monolithic_files) == 1:
        score -= 4
        p, lc = monolithic_files[0]
        findings.append(f"Monolithic file: {Path(p).name} ({lc} lines) — consider refactoring")

    # Duplication penalty
    if duplication_ratio > 0.2:
        score -= 15
        findings.append(f"High code duplication ratio: {duplication_ratio:.1%}")
    elif duplication_ratio > 0.1:
        score -= 8
    elif duplication_ratio > 0.05:
        score -= 3

    # Deep nesting penalty
    if len(deep_functions) > 5:
        score -= 10
        findings.append(f"{len(deep_functions)} functions with nesting depth >4")
    elif len(deep_functions) > 0:
        score -= 5

    # Complex function penalty
    if len(complex_functions) > 5:
        score -= 10
    elif len(complex_functions) > 0:
        score -= 5

    score = max(0, score)

    metrics = {
        "file_count": file_count, "total_lines": total_lines, "function_count": len(all_functions),
        "avg_complexity": round(avg_complexity, 2), "max_complexity": max_complexity,
        "avg_function_length": round(avg_length, 1), "max_function_length": max_length,
        "max_nesting_depth": max_depth, "duplication_ratio": round(duplication_ratio, 3),
        "long_functions": len(long_functions), "complex_functions": len(complex_functions),
        "deep_nesting_functions": len(deep_functions), "parse_errors": parse_errors,
        "monolithic_files": len(monolithic_files),
    }

    # Top offenders
    top_complex = sorted(all_functions, key=lambda x: x["complexity"], reverse=True)[:5]
    top_long = sorted(all_functions, key=lambda x: x["length"], reverse=True)[:5]
    top_monolithic = [{"file": Path(p).name, "lines": lc} for p, lc in monolithic_files[:5]]

    justifications = [{
        "criterion": "code_quality",
        "points": score,
        "evidence": json.dumps(metrics),
        "reasoning": (f"Analyzed {file_count} files, {len(all_functions)} functions. "
                      f"Avg CC={avg_complexity:.1f}, max length={max_length}, "
                      f"duplication={duplication_ratio:.1%}, "
                      f"{len(monolithic_files)} monolithic files (>1000 lines)."),
    }]

    return {
        "domain": "Codebase Optimization", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "metrics": metrics, "top_complex": top_complex, "top_long": top_long,
        "top_monolithic": top_monolithic,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_codebase(target), indent=2))

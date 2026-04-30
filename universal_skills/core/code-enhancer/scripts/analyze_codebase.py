#!/usr/bin/env python3
"""FR-003: Codebase optimization analysis for code-enhancer skill.

Uses the ast module to measure cyclomatic complexity, function length,
nesting depth, duplication, and module coupling.

CONCEPT:CE-003 — Codebase Quality Analysis
"""

import ast
import hashlib
import json
import re
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
                and "node_modules" not in f.parts and ".git" not in f.parts
                and "build" not in f.parts and "dist" not in f.parts
                and ".egg-info" not in str(f)]

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

    # ----------------------------------------------------------------
    # Structural analysis: composite heuristics (replaces >1000L check)
    #
    # Industry-aligned thresholds from:
    #   - Cognitive Complexity (SonarSource): focus on comprehension cost
    #   - SRP (Single Responsibility): measure concept diversity, not lines
    #   - Data vs Code: exclude schema dicts, Pydantic registries, configs
    #
    # Key insight: a 1800-line Pydantic model file with 85 tiny classes
    # is LESS problematic than a 500-line file with 3 unrelated domains.
    # ----------------------------------------------------------------
    file_sizes: dict[str, int] = {}
    for f in py_files:
        try:
            line_count = len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
            file_sizes[str(f)] = line_count
        except Exception:
            pass

    # Classify large files (>500 lines) as data, cohesive, or monolithic
    structural_issues: list[dict] = []
    for filepath_str, line_count in file_sizes.items():
        if line_count < 500:
            continue
        filepath = Path(filepath_str)
        if filepath.name.startswith("test_") or filepath.name == "__init__.py":
            continue

        try:
            source = filepath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=filepath_str)
        except (SyntaxError, UnicodeDecodeError):
            continue

        top_classes = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]
        top_functions = [n for n in ast.iter_child_nodes(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        top_assigns = [n for n in ast.iter_child_nodes(tree)
                       if isinstance(n, (ast.Assign, ast.AnnAssign))]

        # --- Classification 1: Data file ---
        # Files that are essentially one large dict/list literal, or pure
        # Pydantic/StrEnum model registries with high class count + low avg size.
        is_data_file = False
        if len(top_classes) == 0 and len(top_functions) == 0 and len(top_assigns) > 0:
            # Pure data module (e.g., SCHEMA = {...})
            is_data_file = True
        elif len(top_classes) > 20:
            avg_class_lines = line_count / len(top_classes)
            if avg_class_lines < 30:
                # Model registry: many tiny classes (Pydantic, StrEnum, dataclass)
                is_data_file = True

        if is_data_file:
            continue  # Don't penalize data files

        # --- Classification 2: Concept cohesion ---
        # Count distinct "concept domains" from class/function name prefixes
        concept_words: set[str] = set()
        for cls in top_classes:
            words = re.findall(r"[A-Z][a-z]+", cls.name)
            concept_words.update(w.lower() for w in words if len(w) > 3)
        for fn in top_functions:
            parts = fn.name.split("_")
            concept_words.update(p for p in parts if len(p) > 3 and not p.startswith("_"))

        # --- Classification 3: Function-level complexity ---
        # The REAL issue is individual functions that are too long or too complex,
        # not the file being large.
        func_issues: list[dict] = []
        for fn in top_functions:
            end = getattr(fn, "end_lineno", fn.lineno + 1)
            fn_len = end - fn.lineno + 1
            fn_cc = _cyclomatic_complexity(fn)
            # Industry thresholds:
            #   - Function >200 lines: definitely needs splitting
            #   - Function CC > 15: hard to test and maintain
            #   - Function nesting > 4: cognitive overload
            fn_depth = _max_nesting_depth(fn)
            if fn_len > 200 or fn_cc > 15 or fn_depth > 5:
                func_issues.append({
                    "name": fn.name,
                    "lines": fn_len,
                    "complexity": fn_cc,
                    "nesting": fn_depth,
                })

        # Also check methods inside classes
        for cls in top_classes:
            for method in ast.iter_child_nodes(cls):
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end = getattr(method, "end_lineno", method.lineno + 1)
                    m_len = end - method.lineno + 1
                    m_cc = _cyclomatic_complexity(method)
                    m_depth = _max_nesting_depth(method)
                    if m_len > 200 or m_cc > 15 or m_depth > 5:
                        func_issues.append({
                            "name": f"{cls.name}.{method.name}",
                            "lines": m_len,
                            "complexity": m_cc,
                            "nesting": m_depth,
                        })

        # --- Composite scoring: is this file genuinely problematic? ---
        # Criteria for "needs refactoring" (must meet 2+ of these):
        #   1. Has functions/methods >200L or CC>15
        #   2. Concept diversity >5 distinct domains in one file
        #   3. File has >10 top-level public functions (low cohesion)
        #   4. Single class with >20 methods (god class)
        issues = []
        public_functions = [f for f in top_functions if not f.name.startswith("_")]
        god_classes = [(c.name, len([m for m in ast.iter_child_nodes(c)
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]))
                       for c in top_classes]
        god_classes = [(name, count) for name, count in god_classes if count > 20]

        if func_issues:
            top_offender = max(func_issues, key=lambda x: x["lines"])
            issues.append(f"{len(func_issues)} functions with high complexity "
                          f"(worst: {top_offender['name']} at {top_offender['lines']}L, "
                          f"CC={top_offender['complexity']})")
        if len(concept_words) > 8:
            issues.append(f"Low cohesion: {len(concept_words)} distinct concepts in one file")
        if len(public_functions) > 15:
            issues.append(f"{len(public_functions)} public functions — consider grouping into modules")
        if god_classes:
            for name, count in god_classes:
                issues.append(f"God class: {name} ({count} methods) — consider mixins/composition")

        if len(issues) >= 1:  # At least one real structural problem
            structural_issues.append({
                "file": filepath.name,
                "path": filepath_str,
                "lines": line_count,
                "issues": issues,
                "func_issues": func_issues[:5],
                "classification": "monolithic" if len(issues) >= 2 else "needs_attention",
            })

    structural_issues.sort(key=lambda x: len(x["issues"]), reverse=True)

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

    # Long function penalty (>50 lines — informational, >200 lines — actionable)
    very_long_functions = [f for f in all_functions if f["length"] > 200]
    if very_long_functions:
        score -= min(15, len(very_long_functions) * 3)
        findings.append(
            f"{len(very_long_functions)} functions exceed 200 lines (actionable refactoring targets): "
            + ", ".join(f"{f['name']} ({f['length']}L)" for f in
                        sorted(very_long_functions, key=lambda x: -x["length"])[:5])
        )
    elif len(long_functions) > 20:
        score -= 8
        findings.append(f"{len(long_functions)} functions exceed 50 lines")
    elif len(long_functions) > 5:
        score -= 3

    # Structural issues penalty (replaces raw monolithic file count)
    truly_monolithic = [si for si in structural_issues if si["classification"] == "monolithic"]
    needs_attention = [si for si in structural_issues if si["classification"] == "needs_attention"]

    if truly_monolithic:
        score -= min(15, len(truly_monolithic) * 5)
        for si in truly_monolithic[:3]:
            findings.append(
                f"Monolithic: {si['file']} ({si['lines']}L) — "
                + "; ".join(si["issues"][:2])
            )
    if needs_attention:
        score -= min(8, len(needs_attention) * 2)
        for si in needs_attention[:3]:
            findings.append(
                f"Needs attention: {si['file']} ({si['lines']}L) — "
                + si["issues"][0]
            )

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
        "structural_issues": len(structural_issues),
        "truly_monolithic": len([si for si in structural_issues if si["classification"] == "monolithic"]),
    }

    # Top offenders
    top_complex = sorted(all_functions, key=lambda x: x["complexity"], reverse=True)[:5]
    top_long = sorted(all_functions, key=lambda x: x["length"], reverse=True)[:5]

    # Flat directory detection: directories with >15 Python source files
    flat_dirs: list[dict] = []
    checked_dirs: set[str] = set()
    for f in py_files:
        parent = str(f.parent)
        if parent in checked_dirs:
            continue
        checked_dirs.add(parent)
        sibling_py = [
            s for s in f.parent.glob("*.py")
            if s.name != "__init__.py" and not s.name.startswith("test_")
        ]
        if len(sibling_py) > 15:
            flat_dirs.append({
                "directory": str(f.parent.relative_to(root)),
                "python_files": len(sibling_py),
                "suggestion": "Consider organizing into subdirectories by domain/feature",
            })

    if flat_dirs:
        findings.append(
            f"{len(flat_dirs)} flat directories with >15 Python files: "
            + ", ".join(d["directory"] for d in flat_dirs[:3])
        )

    justifications = [{
        "criterion": "code_quality",
        "points": score,
        "evidence": json.dumps(metrics),
        "reasoning": (f"Analyzed {file_count} files, {len(all_functions)} functions. "
                      f"Avg CC={avg_complexity:.1f}, max length={max_length}, "
                      f"duplication={duplication_ratio:.1%}, "
                      f"{len(structural_issues)} structural issues "
                      f"({len([s for s in structural_issues if s['classification']=='monolithic'])} monolithic)."),
    }]

    return {
        "domain": "Codebase Optimization", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "metrics": metrics, "top_complex": top_complex, "top_long": top_long,
        "structural_issues": structural_issues[:10],
        "flat_directories": flat_dirs,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_codebase(target), indent=2))

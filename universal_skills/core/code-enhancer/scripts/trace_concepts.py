#!/usr/bin/env python3
"""FR-008: Concept traceability for code-enhancer skill.

Scans for CONCEPT:CE-XXX markers in code docstrings, docs, and pytest
markers. Enhanced to also detect @pytest.mark.concept("xxx") decorators
via AST, identify tests/functions missing concept markers, and cross-reference
against a concept registry from AGENTS.md.

CONCEPT:CE-008 — Concept Traceability
"""

import ast
import json
import re
import sys
from pathlib import Path

CONCEPT_PATTERN = re.compile(r"CONCEPT:(\S+)")
MARKER_PATTERN = re.compile(r'@pytest\.mark\.concept\(\s*["\'](\S+?)["\']\s*\)')

_SKIP_DIRS = frozenset({
    ".venv", "venv", "__pycache__", "node_modules", ".git",
    "build", "dist", ".tox", ".mypy_cache",
})


def _scan_concepts_in_files(root: Path, glob_pattern: str, source_type: str) -> list[dict]:
    """Scan files for CONCEPT markers via regex."""
    concepts: list[dict] = []
    for f in root.rglob(glob_pattern):
        if any(skip in f.parts for skip in _SKIP_DIRS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in CONCEPT_PATTERN.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            concepts.append({
                "concept_id": match.group(1),
                "file": str(f),
                "line": line_num,
                "source_type": source_type,
            })
    return concepts


def _scan_pytest_decorators(root: Path) -> tuple[list[dict], list[dict]]:
    """Scan test files for @pytest.mark.concept decorators using AST.

    Returns:
        (concepts_found, tests_missing_markers)
    """
    concepts: list[dict] = []
    missing: list[dict] = []

    test_dirs = [root / "tests", root / "test"]
    test_files: list[Path] = []
    for td in test_dirs:
        if td.is_dir():
            test_files.extend(td.rglob("test_*.py"))
            test_files.extend(td.rglob("*_test.py"))
    test_files.extend(root.glob("test_*.py"))
    test_files = list(set(test_files))

    for tf in test_files:
        if any(skip in tf.parts for skip in _SKIP_DIRS):
            continue
        try:
            source = tf.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(tf))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("test_"):
                    continue

                # Check decorators for @pytest.mark.concept(...)
                has_concept = False
                for dec in node.decorator_list:
                    concept_id = _extract_concept_from_decorator(dec)
                    if concept_id:
                        has_concept = True
                        concepts.append({
                            "concept_id": concept_id,
                            "file": str(tf),
                            "line": node.lineno,
                            "source_type": "test_decorator",
                            "test_name": node.name,
                        })

                # Also check docstring and body for CONCEPT: pattern
                end_line = getattr(node, "end_lineno", node.lineno + 1)
                body_lines = source.splitlines()[node.lineno - 1:end_line]
                body_source = "\n".join(body_lines)
                for match in CONCEPT_PATTERN.finditer(body_source):
                    has_concept = True
                    concepts.append({
                        "concept_id": match.group(1),
                        "file": str(tf),
                        "line": node.lineno,
                        "source_type": "test_docstring",
                        "test_name": node.name,
                    })

                if not has_concept:
                    missing.append({
                        "test_name": node.name,
                        "file": str(tf),
                        "line": node.lineno,
                    })

    return concepts, missing


def _extract_concept_from_decorator(dec: ast.AST) -> str | None:
    """Extract concept ID from a @pytest.mark.concept("xxx") decorator."""
    # Pattern: @pytest.mark.concept("AU-001")
    if isinstance(dec, ast.Call):
        func = dec.func
        # Check for pytest.mark.concept(...) pattern
        if (isinstance(func, ast.Attribute) and func.attr == "concept"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "mark"):
            # Extract string argument
            if dec.args and isinstance(dec.args[0], ast.Constant):
                return str(dec.args[0].value)
    return None


def _scan_function_docstrings(root: Path) -> list[dict]:
    """Scan Python functions >10 lines for missing CONCEPT markers in docstrings."""
    missing: list[dict] = []

    for f in root.rglob("*.py"):
        if any(skip in f.parts for skip in _SKIP_DIRS):
            continue
        # Skip test files — they're handled by _scan_pytest_decorators
        if "test_" in f.name or f.name.endswith("_test.py"):
            continue

        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno + 1)
                length = end_line - node.lineno + 1

                # Only check functions >10 lines (significant functions)
                if length < 10:
                    continue

                # Skip private/dunder methods
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                # Check docstring for CONCEPT marker
                docstring = ast.get_docstring(node) or ""
                body_lines = source.splitlines()[node.lineno - 1:end_line]
                body_text = "\n".join(body_lines)

                if not CONCEPT_PATTERN.search(docstring) and not CONCEPT_PATTERN.search(body_text):
                    missing.append({
                        "function": node.name,
                        "file": str(f),
                        "line": node.lineno,
                        "length": length,
                    })

    return missing


def _load_concept_registry(root: Path) -> set[str]:
    """Load known concept IDs from AGENTS.md <!-- CONCEPT:xxx --> comments."""
    registry: set[str] = set()
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        return registry

    try:
        content = agents_md.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return registry

    for match in re.finditer(r"<!--\s*CONCEPT:(\S+)\s*-->", content):
        registry.add(match.group(1))
    # Also match inline CONCEPT: references
    for match in CONCEPT_PATTERN.finditer(content):
        registry.add(match.group(1))

    return registry


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


def trace_concepts(root_dir: str = ".") -> dict:
    """Trace concept IDs across code, docs, and tests. Detect drift.

    Enhanced with:
    - AST-based @pytest.mark.concept() decorator scanning
    - Tests-without-concept-markers detection
    - Functions-without-concept-docstrings detection (>10 lines)
    - Concept registry cross-reference from AGENTS.md
    """
    root = Path(root_dir).resolve()

    # Scan all three sources via regex
    code_concepts = _scan_concepts_in_files(root, "*.py", "code")
    doc_concepts = _scan_concepts_in_files(root, "*.md", "docs")
    test_concepts = []
    for td in [root / "tests", root / "test"]:
        if td.is_dir():
            test_concepts.extend(_scan_concepts_in_files(td, "*.py", "test"))

    # Enhanced: AST-based decorator scanning
    decorator_concepts, tests_missing_markers = _scan_pytest_decorators(root)

    # Enhanced: Functions missing concept docstrings
    functions_missing = _scan_function_docstrings(root)

    # Enhanced: Load concept registry
    registry = _load_concept_registry(root)

    # Merge decorator concepts into test concepts (dedup by concept_id + file + line)
    seen = {(c["concept_id"], c["file"], c["line"]) for c in test_concepts}
    for dc in decorator_concepts:
        key = (dc["concept_id"], dc["file"], dc["line"])
        if key not in seen:
            test_concepts.append(dc)
            seen.add(key)

    all_concepts = code_concepts + doc_concepts + test_concepts

    # Build concept map
    concept_map: dict[str, dict[str, list[dict]]] = {}
    for c in all_concepts:
        cid = c["concept_id"]
        if cid not in concept_map:
            concept_map[cid] = {"code": [], "docs": [], "test": [], "test_decorator": [], "test_docstring": []}
        source = c["source_type"]
        if source in concept_map[cid]:
            concept_map[cid][source].append(c)
        elif source in ("test", "test_decorator", "test_docstring"):
            concept_map[cid]["test"].append(c)

    # Detect orphans and drift
    orphans: list[dict] = []
    drift: list[dict] = []
    well_traced = 0

    for cid, sources in concept_map.items():
        has_code = len(sources["code"]) > 0
        has_docs = len(sources["docs"]) > 0
        has_test = (len(sources["test"]) > 0 or len(sources.get("test_decorator", [])) > 0
                    or len(sources.get("test_docstring", [])) > 0)

        coverage_count = sum([has_code, has_docs, has_test])
        if coverage_count == 3:
            well_traced += 1
        elif coverage_count == 1:
            orphans.append({
                "concept_id": cid,
                "present_in": [k for k, v in sources.items() if v],
                "missing_from": [k for k, v in {"code": sources["code"],
                                                  "docs": sources["docs"],
                                                  "test": sources["test"]}.items() if not v],
            })
        elif coverage_count == 2:
            drift.append({
                "concept_id": cid,
                "present_in": [k for k, v in sources.items() if v],
                "missing_from": [k for k, v in {"code": sources["code"],
                                                  "docs": sources["docs"],
                                                  "test": sources["test"]}.items() if not v],
            })

    # Registry cross-reference: concepts in registry but not in code
    unimplemented = []
    if registry:
        found_concepts = set(concept_map.keys())
        for reg_id in registry:
            if reg_id not in found_concepts:
                unimplemented.append(reg_id)

    # Scoring
    total_concepts = len(concept_map)
    score = 100
    findings: list[str] = []

    if total_concepts == 0:
        score = 30
        findings.append("No CONCEPT markers found — traceability not implemented")
    else:
        trace_ratio = well_traced / total_concepts
        if trace_ratio < 0.3:
            score -= 30
            findings.append(f"Low traceability ratio: {trace_ratio:.0%} concepts fully traced")
        elif trace_ratio < 0.6:
            score -= 15
        elif trace_ratio < 0.8:
            score -= 5

        if len(orphans) > 5:
            score -= 15
            findings.append(f"{len(orphans)} orphaned concepts (only in one source)")
        elif len(orphans) > 0:
            score -= len(orphans) * 2

        if len(drift) > 5:
            score -= 10
            findings.append(f"{len(drift)} concepts with drift (missing from one source)")
        elif len(drift) > 0:
            score -= len(drift)

    # Enhanced: penalty for tests missing concept markers
    if tests_missing_markers:
        penalty = min(20, len(tests_missing_markers) * 2)
        score -= penalty
        findings.append(
            f"{len(tests_missing_markers)} test functions missing concept markers"
        )

    # Enhanced: penalty for functions missing concept docstrings
    if len(functions_missing) > 20:
        score -= 10
        findings.append(
            f"{len(functions_missing)} significant functions (>10 lines) "
            f"missing concept markers in docstrings"
        )
    elif len(functions_missing) > 10:
        score -= 5

    # Enhanced: unimplemented registry concepts
    if unimplemented:
        findings.append(
            f"{len(unimplemented)} concepts in AGENTS.md registry not found in code: "
            + ", ".join(unimplemented[:5])
        )

    score = max(0, score)

    metrics = {
        "total_concepts": total_concepts,
        "well_traced": well_traced,
        "orphans": len(orphans),
        "drift": len(drift),
        "code_concepts": len(code_concepts),
        "doc_concepts": len(doc_concepts),
        "test_concepts": len(test_concepts),
        "decorator_concepts": len(decorator_concepts),
        "tests_missing_markers": len(tests_missing_markers),
        "functions_missing_docstrings": len(functions_missing),
        "registry_concepts": len(registry),
        "unimplemented_concepts": len(unimplemented),
    }

    justifications = [{
        "criterion": "concept_traceability",
        "points": score,
        "evidence": json.dumps(metrics),
        "reasoning": (f"{total_concepts} unique concepts found. "
                      f"{well_traced} fully traced (code+docs+tests), "
                      f"{len(orphans)} orphans, {len(drift)} drifted. "
                      f"{len(tests_missing_markers)} tests without concept markers. "
                      f"{len(functions_missing)} functions without concept docstrings."),
    }]

    return {
        "domain": "Concept Traceability", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "metrics": metrics, "concept_map": {k: {src: len(v) for src, v in sources.items()}
                                             for k, v in concept_map.items() for sources in [v]},
        "orphans": orphans[:10], "drift": drift[:10],
        "tests_missing_markers": tests_missing_markers[:20],
        "functions_missing_docstrings": functions_missing[:20],
        "unimplemented_concepts": unimplemented,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(trace_concepts(target), indent=2))

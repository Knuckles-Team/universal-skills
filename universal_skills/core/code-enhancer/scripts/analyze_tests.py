#!/usr/bin/env python3
"""FR-005: Test coverage analysis for code-enhancer skill.

Inventories pytest tests, maps to use-cases, classifies intent,
and detects drift between docs and tests.

CONCEPT:CE-005 — Test Coverage Analysis
"""

import ast
import json
import re
import sys
from pathlib import Path


def _classify_test_intent(name: str, body_source: str) -> str:
    """Classify test intent based on name and body patterns."""
    name_lower = name.lower()
    if "integration" in name_lower or "e2e" in name_lower or "end_to_end" in name_lower:
        return "integration"
    if "smoke" in name_lower:
        return "smoke"
    if "regression" in name_lower:
        return "regression"
    if "performance" in name_lower or "benchmark" in name_lower:
        return "performance"
    if "mock" in body_source or "patch" in body_source or "MagicMock" in body_source:
        return "unit"
    if "subprocess" in body_source or "requests" in body_source:
        return "integration"
    return "unit"


def _extract_tests_from_file(filepath: Path) -> list[dict]:
    """Extract test function metadata from a Python test file."""
    tests: list[dict] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return tests

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                end_line = getattr(node, "end_lineno", node.lineno + 1)
                body_lines = source.splitlines()[node.lineno - 1:end_line]
                body_source = "\n".join(body_lines)

                # Extract markers
                markers: list[str] = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if dec.func.attr == "mark":
                            markers.append("mark")
                        elif isinstance(dec.func.value, ast.Attribute):
                            markers.append(dec.func.attr)
                    elif isinstance(dec, ast.Attribute):
                        markers.append(dec.attr)

                # Check for concept markers
                concept_id = ""
                concept_match = re.search(r"CONCEPT:(\S+)", body_source)
                if concept_match:
                    concept_id = concept_match.group(1)

                intent = _classify_test_intent(node.name, body_source)
                tests.append({
                    "name": node.name,
                    "file": str(filepath),
                    "line": node.lineno,
                    "length": end_line - node.lineno + 1,
                    "intent": intent,
                    "markers": markers,
                    "concept_id": concept_id,
                    "has_assertions": "assert" in body_source,
                })
    return tests


def _detect_doc_test_drift(root: Path, tests: list[dict]) -> list[dict]:
    """Detect drift between documented features and test coverage."""
    drift: list[dict] = []
    # Check if README mentions features not covered by tests
    readme = root / "README.md"
    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8", errors="ignore").lower()
        test_names_lower = " ".join(t["name"].lower() for t in tests)

        # Simple heuristic: look for feature-like headings
        features = re.findall(r"##\s+(.+)", readme_text)
        for feature in features:
            feature_words = set(feature.strip().split())
            # Check if any test name references this feature
            if not any(w in test_names_lower for w in feature_words if len(w) > 4):
                drift.append({
                    "type": "untested_feature",
                    "source": "README.md",
                    "feature": feature.strip(),
                    "detail": "Feature heading in README has no corresponding test",
                })
    return drift


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


def analyze_tests(root_dir: str = ".") -> dict:
    """Analyze test suite quality and coverage."""
    root = Path(root_dir).resolve()

    # Find test files
    test_dirs = [root / "tests", root / "test"]
    test_files: list[Path] = []
    for td in test_dirs:
        if td.is_dir():
            test_files.extend(td.rglob("test_*.py"))
            test_files.extend(td.rglob("*_test.py"))
    # Also check root for test files
    test_files.extend(root.glob("test_*.py"))
    test_files = list(set(test_files))

    if not test_files:
        return {"domain": "Test Coverage", "score": 20, "grade": "F",
                "findings": ["No test files found"],
                "justifications": [{"criterion": "test_existence", "points": 0,
                    "evidence": str(root), "reasoning": "No test files found in tests/ or test/ directories"}],
                "metrics": {}, "tests": []}

    # Extract all tests
    all_tests: list[dict] = []
    for tf in test_files:
        all_tests.extend(_extract_tests_from_file(tf))

    # Classify
    intent_counts: dict[str, int] = {}
    for t in all_tests:
        intent_counts[t["intent"]] = intent_counts.get(t["intent"], 0) + 1

    # Check assertion coverage
    no_assert = [t for t in all_tests if not t["has_assertions"]]
    concept_tests = [t for t in all_tests if t["concept_id"]]

    # Count source files for ratio
    src_files = [f for f in root.rglob("*.py")
                 if "test" not in f.parts and ".venv" not in f.parts
                 and "__pycache__" not in f.parts and ".git" not in f.parts]

    test_to_src_ratio = len(all_tests) / max(len(src_files), 1)

    # Drift detection
    drift_items = _detect_doc_test_drift(root, all_tests)

    # Scoring
    score = 100
    findings: list[str] = []

    # Test count relative to source
    if test_to_src_ratio < 0.3:
        score -= 20
        findings.append(f"Low test-to-source ratio: {test_to_src_ratio:.2f}")
    elif test_to_src_ratio < 0.5:
        score -= 10
    elif test_to_src_ratio < 1.0:
        score -= 5

    # No-assert tests
    if len(no_assert) > 5:
        score -= 15
        findings.append(f"{len(no_assert)} tests without assertions")
    elif len(no_assert) > 0:
        score -= 5

    # Intent diversity (good to have both unit and integration)
    if len(intent_counts) < 2:
        score -= 10
        findings.append("Test suite lacks intent diversity (only one type)")

    # Drift
    if len(drift_items) > 5:
        score -= 10
        findings.append(f"{len(drift_items)} potential doc-test drift items")
    elif len(drift_items) > 0:
        score -= 5

    score = max(0, score)

    metrics = {
        "test_file_count": len(test_files),
        "test_count": len(all_tests),
        "source_file_count": len(src_files),
        "test_to_source_ratio": round(test_to_src_ratio, 2),
        "intent_distribution": intent_counts,
        "tests_without_assertions": len(no_assert),
        "concept_traced_tests": len(concept_tests),
        "drift_items": len(drift_items),
    }

    justifications = [{
        "criterion": "test_coverage_quality",
        "points": score,
        "evidence": json.dumps(metrics),
        "reasoning": (f"{len(all_tests)} tests across {len(test_files)} files. "
                      f"Ratio: {test_to_src_ratio:.2f}. "
                      f"Intent: {intent_counts}. "
                      f"{len(no_assert)} without assertions, {len(drift_items)} drift items."),
    }]

    return {
        "domain": "Test Coverage", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "metrics": metrics, "tests": all_tests[:30], "drift": drift_items[:10],
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_tests(target), indent=2))

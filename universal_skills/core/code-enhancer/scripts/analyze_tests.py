#!/usr/bin/env python3
"""FR-005: Test coverage analysis for code-enhancer skill.

Inventories pytest tests, maps to use-cases, classifies intent,
and detects drift between docs and tests.

KG-native (CE-045): test symbol discovery goes through the graph-os code KG first
(``kg_native.repo_symbols`` — a repo already ingested has ``is_test``/decorator/
assert-count data for free), then the engine tree-sitter AST, and only falls back
to a local stdlib ``ast`` parse when neither is reachable.

CONCEPT:CE-005 — Test Coverage Analysis
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kg_native import (  # noqa: E402 - needs the sys.path insert above
    body_span,
    file_symbols_by_line,
    kg_repo_symbols,
    split_decorators,
)


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


def _decorator_markers(decorators: str) -> list[str]:
    """Marker names from a symbol's joined ``decorators`` — the last dotted segment
    of each (``pytest.mark.parametrize(...)`` -> ``parametrize``, ``pytest.fixture``
    -> ``fixture``). Informational only (not scored), so a lightweight regex over
    the already-extracted decorator text replaces the old nested ast.Call/Attribute
    walk."""
    markers: list[str] = []
    for d in split_decorators(decorators):
        d = d.lstrip("@").strip()
        name = re.split(r"\(", d, maxsplit=1)[0]
        if name:
            markers.append(name.rsplit(".", 1)[-1])
    return markers


def _extract_tests_from_file(
    filepath: Path, kg_symbols: list[dict] | None = None
) -> list[dict]:
    """Extract test function metadata from a Python test file.

    KG-native (CE-045): ``kg_symbols`` — when the caller already bulk-fetched them
    from the graph-os code KG (Tier 1) for the whole repo — is used as-is; otherwise
    falls back to the tiered per-file ``kg_native`` retrieval (engine AST, then a
    local ``ast`` parse) instead of a direct ``ast.walk`` here.
    """
    tests: list[dict] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return tests
    source_lines = source.splitlines()

    raw_symbols = (
        sorted(kg_symbols, key=lambda s: int(s.get("line") or 0))
        if kg_symbols is not None
        else file_symbols_by_line(filepath)
    )
    symbols = [
        s
        for s in raw_symbols
        if s.get("kind_detail", "").lower() in ("function", "method")
        and str(s.get("name", "")).startswith("test_")
    ]
    for i, sym in enumerate(symbols):
        name = str(sym.get("name", ""))
        line, end_line = body_span(source_lines, symbols, i)
        body_source = "\n".join(source_lines[line - 1 : end_line])

        markers = _decorator_markers(str(sym.get("decorators", "")))

        concept_id = ""
        concept_match = re.search(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)", body_source)
        if concept_match:
            concept_id = concept_match.group(1)

        intent = _classify_test_intent(name, body_source)

        # ACCURACY FIX: precise assertion detection (engine/local assert_count is
        # real `ast.Assert` node counting, not a naive "assert" in body_source
        # substring match, which matches comments/docstrings/variable names).
        try:
            has_assertions = int(sym.get("assert_count") or 0) > 0
        except (TypeError, ValueError):
            has_assertions = False
        if not has_assertions:
            try:
                has_assertions = int(sym.get("raises_count") or 0) > 0
            except (TypeError, ValueError):
                has_assertions = False
        if not has_assertions:
            has_assertions = (
                "pytest.raises" in body_source
                or ".assert_called" in body_source
                or ".assert_any_call" in body_source
            )

        tests.append(
            {
                "name": name,
                "file": str(filepath),
                "line": line,
                "length": end_line - line + 1,
                "intent": intent,
                "markers": markers,
                "concept_id": concept_id,
                "has_assertions": has_assertions,
            }
        )
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
                drift.append(
                    {
                        "type": "untested_feature",
                        "source": "README.md",
                        "feature": feature.strip(),
                        "detail": "Feature heading in README has no corresponding test",
                    }
                )
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
        return {
            "domain": "Test Coverage",
            "score": 20,
            "grade": "F",
            "findings": ["No test files found"],
            "justifications": [
                {
                    "criterion": "test_existence",
                    "points": 0,
                    "evidence": str(root),
                    "reasoning": "No test files found in tests/ or test/ directories",
                }
            ],
            "metrics": {},
            "tests": [],
        }

    # KG-native (CE-045): one bulk repo-scoped Cypher query (Tier 1) beats N
    # per-file engine/local parses when this repo is already ingested.
    kg_symbols = kg_repo_symbols(root)
    kg_by_file: dict[str, list[dict]] = {}
    if kg_symbols:
        for s in kg_symbols:
            kg_by_file.setdefault(str(s.get("file_path", "")), []).append(s)

    # Extract all tests
    all_tests: list[dict] = []
    for tf in test_files:
        all_tests.extend(
            _extract_tests_from_file(tf, kg_symbols=kg_by_file.get(str(tf)))
        )

    # Classify
    intent_counts: dict[str, int] = {}
    for t in all_tests:
        intent_counts[t["intent"]] = intent_counts.get(t["intent"], 0) + 1

    # Check assertion coverage
    no_assert = [t for t in all_tests if not t["has_assertions"]]
    concept_tests = [t for t in all_tests if t["concept_id"]]

    # Count source files for ratio
    src_files = [
        f
        for f in root.rglob("*.py")
        if "test" not in f.parts
        and ".venv" not in f.parts
        and "__pycache__" not in f.parts
        and ".git" not in f.parts
    ]

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

    justifications = [
        {
            "criterion": "test_coverage_quality",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"{len(all_tests)} tests across {len(test_files)} files. "
                f"Ratio: {test_to_src_ratio:.2f}. "
                f"Intent: {intent_counts}. "
                f"{len(no_assert)} without assertions, {len(drift_items)} drift items."
            ),
        }
    ]

    return {
        "domain": "Test Coverage",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "metrics": metrics,
        "tests": all_tests[:30],
        "drift": drift_items[:10],
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_tests(target), indent=2))

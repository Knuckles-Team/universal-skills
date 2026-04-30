#!/usr/bin/env python3
"""CE-024: Pytest grading for code-enhancer skill.

Grades pytest suites against industry best practices using the F.I.R.S.T.
rubric (Fast, Independent, Repeatable, Self-validating, Timely), AAA pattern
compliance, fixture/parametrize usage, organization, and AI slop detection.

CONCEPT:CE-024 — Pytest Quality Grading
"""

import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


# Patterns that indicate generic/AI-generated test names
GENERIC_NAME_PATTERNS = [
    r"^test_\d+$",
    r"^test_case_\d+$",
    r"^test_it$",
    r"^test_main$",
    r"^test_func$",
    r"^test_method$",
    r"^test_run$",
    r"^test_basic$",
]

# Generic assertion patterns (weak assertions)
WEAK_ASSERTIONS = [
    "assert result is not None",
    "assert result",
    "assert True",
    "assert response",
    "assert output",
    "assert data",
    "assert ret",
]


def _analyze_test_file(filepath: Path) -> dict:
    """Analyze a single test file for quality metrics."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return {"error": f"Cannot parse {filepath}", "tests": []}

    lines = source.splitlines()
    tests: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue

        end_line = getattr(node, "end_lineno", node.lineno + 1)
        body_lines = lines[node.lineno - 1 : end_line]
        body_source = "\n".join(body_lines)

        # Count assertions
        assertion_count = body_source.count("assert ")
        assertion_count += body_source.count("pytest.raises")
        assertion_count += body_source.count(".assert_called")
        assertion_count += body_source.count(".assert_any_call")

        # Count mocks
        mock_count = (
            body_source.count("MagicMock")
            + body_source.count("AsyncMock")
            + body_source.count("patch(")
            + body_source.count("mocker.")
            + body_source.count("monkeypatch.")
        )

        # Check for parametrize decorator
        has_parametrize = any(
            "parametrize" in ast.dump(d) for d in node.decorator_list
        )

        # Check for fixture usage (arguments beyond self/cls)
        fixture_args = [
            a.arg
            for a in node.args.args
            if a.arg not in ("self", "cls")
        ]

        # Name quality
        name_len = len(node.name)
        is_generic = any(
            re.match(p, node.name) for p in GENERIC_NAME_PATTERNS
        )
        is_descriptive = name_len > 15 and "_" in node.name[5:]

        # Weak assertions
        weak_assert_count = sum(
            1 for wa in WEAK_ASSERTIONS if wa in body_source
        )

        # Body hash for duplication detection
        # Normalize: strip whitespace, remove function name line
        normalized = "\n".join(
            line.strip()
            for line in body_lines[1:]
            if line.strip() and not line.strip().startswith("#")
        )
        body_hash = hashlib.md5(normalized.encode()).hexdigest()

        tests.append(
            {
                "name": node.name,
                "file": str(filepath),
                "line": node.lineno,
                "length": end_line - node.lineno + 1,
                "assertion_count": assertion_count,
                "mock_count": mock_count,
                "has_parametrize": has_parametrize,
                "fixture_args": fixture_args,
                "is_generic_name": is_generic,
                "is_descriptive_name": is_descriptive,
                "weak_assert_count": weak_assert_count,
                "body_hash": body_hash,
            }
        )

    return {
        "file": str(filepath),
        "total_lines": len(lines),
        "test_count": len(tests),
        "tests": tests,
    }


def _check_conftest(root: Path) -> dict:
    """Check for conftest.py files and their quality."""
    conftest_files = list(root.rglob("conftest.py"))
    # Filter out .venv, __pycache__, etc.
    conftest_files = [
        f
        for f in conftest_files
        if ".venv" not in f.parts and "__pycache__" not in f.parts
    ]

    total_fixtures = 0
    for cf in conftest_files:
        try:
            source = cf.read_text(encoding="utf-8", errors="ignore")
            total_fixtures += source.count("@pytest.fixture")
            total_fixtures += source.count("@fixture")
        except Exception:
            pass

    return {
        "conftest_count": len(conftest_files),
        "total_shared_fixtures": total_fixtures,
        "has_root_conftest": (root / "tests" / "conftest.py").exists()
        or (root / "conftest.py").exists(),
    }


def _detect_duplicate_tests(all_tests: list[dict]) -> list[dict]:
    """Detect duplicate or near-duplicate test bodies."""
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for t in all_tests:
        if t.get("length", 0) > 3:  # Skip trivially short tests
            hash_groups[t["body_hash"]].append(t["name"])

    duplicates = []
    for body_hash, names in hash_groups.items():
        if len(names) > 1:
            duplicates.append(
                {
                    "hash": body_hash,
                    "count": len(names),
                    "tests": names[:5],
                }
            )

    return duplicates


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


def grade_pytest(root_dir: str = ".") -> dict:
    """Grade pytest test suite against best practices.

    Scoring breakdown (100 pts total):
    - 20 pts: Naming quality
    - 20 pts: Structure & organization
    - 20 pts: Fixture/parametrize usage
    - 20 pts: Assertion quality
    - 20 pts: No AI slop indicators
    """
    root = Path(root_dir).resolve()

    # Find test files
    test_dirs = [root / "tests", root / "test"]
    test_files: list[Path] = []
    for td in test_dirs:
        if td.is_dir():
            test_files.extend(td.rglob("test_*.py"))
            test_files.extend(td.rglob("*_test.py"))
    test_files.extend(root.glob("test_*.py"))
    test_files = list(
        {
            f
            for f in test_files
            if ".venv" not in f.parts and "__pycache__" not in f.parts
        }
    )

    if not test_files:
        return {
            "domain": "Pytest Quality",
            "score": 0,
            "grade": "F",
            "findings": ["No test files found"],
            "justifications": [
                {
                    "criterion": "pytest_quality",
                    "points": 0,
                    "evidence": str(root),
                    "reasoning": "No test files found in tests/ or test/ directories",
                }
            ],
            "metrics": {"test_files": 0, "total_tests": 0},
        }

    # Analyze all test files
    all_tests: list[dict] = []
    large_files: list[dict] = []
    dense_files: list[dict] = []

    for tf in test_files:
        result = _analyze_test_file(tf)
        if "error" in result:
            continue
        all_tests.extend(result["tests"])

        if result["total_lines"] > 500:
            large_files.append(
                {"file": str(tf.name), "lines": result["total_lines"]}
            )
        if result["test_count"] > 30:
            dense_files.append(
                {"file": str(tf.name), "test_count": result["test_count"]}
            )

    if not all_tests:
        return {
            "domain": "Pytest Quality",
            "score": 10,
            "grade": "F",
            "findings": ["Test files exist but contain no test functions"],
            "justifications": [],
            "metrics": {"test_files": len(test_files), "total_tests": 0},
        }

    # Check conftest
    conftest_info = _check_conftest(root)

    # Detect duplicates
    duplicates = _detect_duplicate_tests(all_tests)

    # --- Scoring ---
    findings: list[str] = []

    # 1. Naming quality (20 pts)
    naming_score = 20
    generic_count = sum(1 for t in all_tests if t["is_generic_name"])
    descriptive_count = sum(1 for t in all_tests if t["is_descriptive_name"])
    descriptive_ratio = descriptive_count / len(all_tests)

    if generic_count > 0:
        naming_score -= min(10, generic_count * 2)
        findings.append(
            f"{generic_count} tests have generic names (test_1, test_case_42, etc.)"
        )
    if descriptive_ratio < 0.5:
        naming_score -= 5
        findings.append(
            f"Only {descriptive_ratio:.0%} of tests have descriptive names (>15 chars)"
        )
    elif descriptive_ratio < 0.8:
        naming_score -= 2

    # 2. Structure & organization (20 pts)
    structure_score = 20

    if large_files:
        structure_score -= min(10, len(large_files) * 3)
        findings.append(
            f"{len(large_files)} test files exceed 500 lines — "
            f"split into focused modules"
        )
    if dense_files:
        structure_score -= min(5, len(dense_files) * 2)
        findings.append(
            f"{len(dense_files)} test files have >30 tests — too dense"
        )

    # Check for subdirectory organization
    test_dir = root / "tests"
    if test_dir.is_dir():
        subdirs = [
            d
            for d in test_dir.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ]
        if not subdirs and len(test_files) > 5:
            structure_score -= 3
            findings.append(
                "Test directory lacks subdirectory organization "
                "(consider unit/, integration/, e2e/)"
            )

    if not conftest_info["has_root_conftest"] and len(all_tests) > 10:
        structure_score -= 2
        findings.append("Missing conftest.py for shared fixtures")

    # 3. Fixture/parametrize usage (20 pts)
    fixture_score = 20

    fixture_users = sum(1 for t in all_tests if len(t["fixture_args"]) > 0)
    fixture_ratio = fixture_users / len(all_tests)
    parametrize_users = sum(1 for t in all_tests if t["has_parametrize"])

    if fixture_ratio < 0.2 and len(all_tests) > 10:
        fixture_score -= 8
        findings.append(
            f"Low fixture usage: only {fixture_ratio:.0%} of tests use fixtures"
        )
    elif fixture_ratio < 0.4:
        fixture_score -= 4

    if parametrize_users == 0 and len(all_tests) > 10:
        fixture_score -= 5
        findings.append(
            "No @pytest.mark.parametrize usage — consider data-driven tests"
        )

    if conftest_info["total_shared_fixtures"] == 0 and len(all_tests) > 10:
        fixture_score -= 4
        findings.append("No shared fixtures in conftest.py")

    # 4. Assertion quality (20 pts)
    assertion_score = 20

    no_assert = sum(1 for t in all_tests if t["assertion_count"] == 0)
    weak_assert = sum(1 for t in all_tests if t["weak_assert_count"] > 0)
    high_assert = sum(1 for t in all_tests if t["assertion_count"] > 5)

    if no_assert > 0:
        assertion_score -= min(10, no_assert * 2)
        findings.append(f"{no_assert} tests have no assertions")

    if weak_assert > 3:
        assertion_score -= min(5, weak_assert)
        findings.append(
            f"{weak_assert} tests use weak assertions "
            f"(assert result is not None, assert True, etc.)"
        )

    if high_assert > len(all_tests) * 0.3:
        assertion_score -= 3
        findings.append(
            f"{high_assert} tests have >5 assertions — "
            f"consider splitting (single responsibility)"
        )

    # 5. AI slop detection (20 pts)
    slop_score = 20

    if duplicates:
        total_dups = sum(d["count"] for d in duplicates)
        slop_score -= min(10, total_dups)
        findings.append(
            f"{len(duplicates)} groups of duplicate test bodies detected "
            f"({total_dups} total) — use parametrize instead"
        )

    over_mocked = sum(1 for t in all_tests if t["mock_count"] > 5)
    if over_mocked > 3:
        slop_score -= min(5, over_mocked)
        findings.append(
            f"{over_mocked} tests have excessive mocking (>5 mocks) — "
            f"test behavior, not implementation"
        )

    # Check for very long tests (>100 lines)
    very_long = sum(1 for t in all_tests if t["length"] > 100)
    if very_long > 0:
        slop_score -= min(5, very_long * 2)
        findings.append(
            f"{very_long} tests exceed 100 lines — "
            f"likely doing too much per test"
        )

    # Total score
    total_score = max(
        0,
        naming_score + structure_score + fixture_score + assertion_score + slop_score,
    )

    metrics = {
        "test_files": len(test_files),
        "total_tests": len(all_tests),
        "descriptive_name_ratio": round(descriptive_ratio, 2),
        "generic_names": generic_count,
        "fixture_usage_ratio": round(fixture_ratio, 2),
        "parametrize_users": parametrize_users,
        "conftest_fixtures": conftest_info["total_shared_fixtures"],
        "no_assertion_tests": no_assert,
        "weak_assertion_tests": weak_assert,
        "duplicate_groups": len(duplicates),
        "large_files": len(large_files),
        "over_mocked_tests": over_mocked,
        "very_long_tests": very_long,
        "subscores": {
            "naming": naming_score,
            "structure": structure_score,
            "fixtures": fixture_score,
            "assertions": assertion_score,
            "ai_slop": slop_score,
        },
    }

    justifications = [
        {
            "criterion": "pytest_quality",
            "points": total_score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"{len(all_tests)} tests across {len(test_files)} files. "
                f"Naming: {naming_score}/20, Structure: {structure_score}/20, "
                f"Fixtures: {fixture_score}/20, Assertions: {assertion_score}/20, "
                f"AI Slop: {slop_score}/20."
            ),
        }
    ]

    return {
        "domain": "Pytest Quality",
        "score": total_score,
        "grade": _score_to_grade(total_score),
        "findings": findings,
        "justifications": justifications,
        "metrics": metrics,
        "conftest": conftest_info,
        "duplicates": duplicates[:10],
        "large_files": large_files,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(grade_pytest(target), indent=2))

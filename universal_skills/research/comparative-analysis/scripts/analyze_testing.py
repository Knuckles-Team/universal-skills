#!/usr/bin/env python3
"""CA-006: Testing analysis — test suite, coverage, pyramid, F.I.R.S.T.

Usage: python analyze_testing.py /path/to/project

CONCEPT:CA-006 — Testing & Reliability
"""

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"}

TEST_FRAMEWORKS = {
    "pytest": ["pytest", "conftest.py"],
    "unittest": ["unittest", "TestCase"],
    "jest": ["jest", "describe(", "it("],
    "mocha": ["mocha", "describe("],
    "go_test": ["_test.go"],
    "cargo_test": ["#[test]", "#[cfg(test)]"],
}


def discover_tests(project_path: Path) -> dict:
    """Discover test files and classify by type."""
    test_files = {"unit": [], "integration": [], "e2e": [], "other": []}
    total_test_count = 0
    code_loc = 0
    test_loc = 0

    for f in project_path.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue

        rel_str = str(rel).lower()
        is_test = (
            f.name.startswith("test_")
            or f.name.endswith("_test.py")
            or f.name.endswith(".test.js")
            or f.name.endswith(".test.ts")
            or f.name.endswith("_test.go")
            or "tests/" in rel_str
            or "test/" in rel_str
            or "__tests__/" in rel_str
            or "spec/" in rel_str
        )

        if f.suffix in {".py", ".js", ".ts", ".go", ".rs", ".java"}:
            try:
                loc = sum(1 for _ in open(f, errors="ignore"))
            except (OSError, UnicodeDecodeError):
                loc = 0

            if is_test:
                test_loc += loc
                # Classify
                if "integration" in rel_str or "integ" in rel_str:
                    test_files["integration"].append(str(rel))
                elif (
                    "e2e" in rel_str
                    or "end_to_end" in rel_str
                    or "acceptance" in rel_str
                ):
                    test_files["e2e"].append(str(rel))
                elif "unit" in rel_str or f.name.startswith("test_"):
                    test_files["unit"].append(str(rel))
                else:
                    test_files["other"].append(str(rel))

                # Count test functions
                if f.suffix == ".py":
                    try:
                        content = f.read_text(errors="ignore")
                        total_test_count += len(re.findall(r"def test_", content))
                    except Exception:
                        pass
                elif f.suffix in {".js", ".ts"}:
                    try:
                        content = f.read_text(errors="ignore")
                        total_test_count += len(re.findall(r"\bit\(|test\(", content))
                    except Exception:
                        pass
            else:
                code_loc += loc

    return {
        "test_files": {k: len(v) for k, v in test_files.items()},
        "total_test_files": sum(len(v) for v in test_files.values()),
        "total_test_functions": total_test_count,
        "code_loc": code_loc,
        "test_loc": test_loc,
        "test_to_code_ratio": round(test_loc / max(code_loc, 1), 2),
    }


def detect_framework(project_path: Path) -> str:
    """Detect the primary test framework."""
    for f in ["pyproject.toml", "setup.cfg", "tox.ini"]:
        p = project_path / f
        if p.exists():
            try:
                if "pytest" in p.read_text(errors="ignore"):
                    return "pytest"
            except Exception:
                pass
    if (project_path / "jest.config.js").exists() or (
        project_path / "jest.config.ts"
    ).exists():
        return "jest"
    if list(project_path.rglob("*_test.go")):
        return "go_test"
    if list(project_path.rglob("*.test.js")) or list(project_path.rglob("*.test.ts")):
        return "jest"
    return "unknown"


def check_test_quality(project_path: Path) -> dict:
    """Check test quality indicators."""
    quality = {
        "has_conftest": (project_path / "tests" / "conftest.py").exists()
        or (project_path / "conftest.py").exists(),
        "has_fixtures": False,
        "has_parametrize": False,
        "has_markers": False,
        "has_mocks": False,
        "timeout_configured": False,
    }

    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = f.read_text(errors="ignore")
            if "@pytest.fixture" in content:
                quality["has_fixtures"] = True
            if "@pytest.mark.parametrize" in content:
                quality["has_parametrize"] = True
            if "@pytest.mark." in content:
                quality["has_markers"] = True
            if "mock" in content.lower() or "patch" in content:
                quality["has_mocks"] = True
            if "timeout" in content.lower():
                quality["timeout_configured"] = True
        except (OSError, UnicodeDecodeError):
            pass

    return quality


def score_testing(tests: dict, framework: str, quality: dict) -> dict:
    """Calculate 0-100 testing score."""
    score = 0
    details = []

    # Test presence (20 points)
    total_files = tests.get("total_test_files", 0)
    if total_files >= 10:
        score += 20
        details.append(f"Comprehensive test suite ({total_files} files): +20")
    elif total_files >= 5:
        score += 15
        details.append(f"Good test suite ({total_files} files): +15")
    elif total_files >= 1:
        score += 10
        details.append(f"Tests present ({total_files} files): +10")
    else:
        details.append("No tests found: +0")

    # Test count (20 points)
    total_tests = tests.get("total_test_functions", 0)
    if total_tests >= 100:
        score += 20
        details.append(f"Many tests ({total_tests}): +20")
    elif total_tests >= 50:
        score += 15
        details.append(f"Good test count ({total_tests}): +15")
    elif total_tests >= 10:
        score += 10
        details.append(f"Some tests ({total_tests}): +10")

    # Test-to-code ratio (20 points)
    ratio = tests.get("test_to_code_ratio", 0)
    if ratio >= 1.0:
        score += 20
        details.append(f"Excellent test ratio ({ratio}:1): +20")
    elif ratio >= 0.5:
        score += 15
        details.append(f"Good ratio ({ratio}:1): +15")
    elif ratio >= 0.2:
        score += 10
        details.append(f"Low ratio ({ratio}:1): +10")

    # Testing pyramid (20 points)
    unit = tests["test_files"].get("unit", 0)
    integ = tests["test_files"].get("integration", 0)
    e2e = tests["test_files"].get("e2e", 0)
    if unit > 0 and integ > 0:
        score += 15
        details.append(
            f"Multi-layer testing (unit:{unit}, integ:{integ}, e2e:{e2e}): +15"
        )
        if unit > integ >= e2e:
            score += 5
            details.append("Proper testing pyramid shape: +5")
    elif unit > 0:
        score += 10
        details.append("Unit tests present: +10")

    # Quality indicators (20 points)
    q_score = 0
    for key in [
        "has_conftest",
        "has_fixtures",
        "has_parametrize",
        "has_markers",
        "timeout_configured",
    ]:
        if quality.get(key):
            q_score += 4
    score += q_score
    details.append(f"Quality indicators ({q_score}/20): +{q_score}")

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
    return {"score": min(score, 100), "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_testing.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    tests = discover_tests(project_path)
    framework = detect_framework(project_path)
    quality = check_test_quality(project_path)
    scoring = score_testing(tests, framework, quality)

    print(
        json.dumps(
            {
                "domain": "CA-006",
                "domain_name": "Testing",
                "project": str(project_path),
                "test_discovery": tests,
                "framework": framework,
                "quality_indicators": quality,
                "scoring": scoring,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

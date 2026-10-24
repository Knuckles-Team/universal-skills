#!/usr/bin/env python3
"""CE-016: Test execution and grading for code-enhancer skill.

Detects the project's test framework, executes tests with a 300-second
global timeout, and grades based on pass/fail ratios. Each failure is
captured as a structured finding for SDD handoff.

Supports: Python (pytest), Go (go test), Node (npm test), Rust (cargo test),
Java (maven/gradle).

CONCEPT:CE-016 — Test Execution
"""

import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_TIMEOUT = 300  # seconds — global default


def _run_tool(
    cmd: list[str], cwd: str, timeout: int = DEFAULT_TIMEOUT
) -> tuple[int, str, str]:
    """Run a CLI tool and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", f"Test execution timed out after {timeout}s"


def _detect_test_framework(root: Path) -> list[dict]:
    """Detect available test frameworks from project files."""
    frameworks: list[dict] = []

    # Python: pytest
    pyproject = root / "pyproject.toml"
    has_tests_dir = (root / "tests").is_dir() or (root / "test").is_dir()
    if pyproject.exists() or has_tests_dir:
        try:
            content = (
                pyproject.read_text(encoding="utf-8", errors="ignore")
                if pyproject.exists()
                else ""
            )
        except Exception:
            content = ""
        if "pytest" in content or has_tests_dir:
            frameworks.append(
                {
                    "language": "python",
                    "framework": "pytest",
                    "command": [
                        "python",
                        "-m",
                        "pytest",
                        "--tb=line",
                        "-q",
                        f"--timeout={DEFAULT_TIMEOUT}",
                        "--no-header",
                    ],
                }
            )

    # Go
    if (root / "go.mod").exists():
        frameworks.append(
            {
                "language": "go",
                "framework": "go test",
                "command": [
                    "go",
                    "test",
                    "./...",
                    f"-timeout={DEFAULT_TIMEOUT}s",
                    "-count=1",
                    "-short",
                ],
            }
        )

    # Node
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
            if "test" in pkg.get("scripts", {}):
                test_script = pkg["scripts"]["test"]
                # Determine if it's jest, vitest, mocha, etc.
                framework = "npm test"
                if "vitest" in test_script:
                    framework = "vitest"
                elif "jest" in test_script:
                    framework = "jest"
                elif "mocha" in test_script:
                    framework = "mocha"
                frameworks.append(
                    {
                        "language": "node",
                        "framework": framework,
                        "command": ["npm", "test", "--", "--watchAll=false"],
                    }
                )
        except (json.JSONDecodeError, Exception):
            pass

    # Rust
    if (root / "Cargo.toml").exists():
        frameworks.append(
            {
                "language": "rust",
                "framework": "cargo test",
                "command": ["cargo", "test", "--no-fail-fast"],
            }
        )

    # Java — Maven
    if (root / "pom.xml").exists():
        frameworks.append(
            {
                "language": "java",
                "framework": "maven",
                "command": ["mvn", "test", "-q", "--batch-mode"],
            }
        )
    # Java — Gradle
    elif (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        frameworks.append(
            {
                "language": "java",
                "framework": "gradle",
                "command": ["./gradlew", "test", "--no-daemon"],
            }
        )

    return frameworks


def _parse_pytest_output(stdout: str, stderr: str) -> dict:
    """Parse pytest -q output for pass/fail/error counts."""
    combined = stdout + "\n" + stderr
    result = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "warnings": 0,
        "skipped": 0,
        "failures": [],
    }

    # Match summary line: "X passed, Y failed, Z error in Ns"
    summary = re.search(r"(\d+)\s+passed", combined)
    if summary:
        result["passed"] = int(summary.group(1))

    failed_match = re.search(r"(\d+)\s+failed", combined)
    if failed_match:
        result["failed"] = int(failed_match.group(1))

    error_match = re.search(r"(\d+)\s+error", combined)
    if error_match:
        result["errors"] = int(error_match.group(1))

    warning_match = re.search(r"(\d+)\s+warning", combined)
    if warning_match:
        result["warnings"] = int(warning_match.group(1))

    skipped_match = re.search(r"(\d+)\s+skipped", combined)
    if skipped_match:
        result["skipped"] = int(skipped_match.group(1))

    # Extract individual failure details
    failure_pattern = re.compile(r"FAILED\s+(\S+)")
    for match in failure_pattern.finditer(combined):
        result["failures"].append(match.group(1))

    return result


def _parse_go_test_output(stdout: str, stderr: str) -> dict:
    """Parse go test output."""
    combined = stdout + "\n" + stderr
    result = {"passed": 0, "failed": 0, "errors": 0, "failures": []}

    passed = len(re.findall(r"^ok\s+", combined, re.MULTILINE))
    failed_lines = re.findall(r"^FAIL\s+(\S+)", combined, re.MULTILINE)
    result["passed"] = passed
    result["failed"] = len(failed_lines)
    result["failures"] = failed_lines

    if "build failed" in combined.lower() or "cannot find" in combined.lower():
        result["errors"] = 1

    return result


def _parse_generic_output(stdout: str, stderr: str, rc: int) -> dict:
    """Parse generic test output based on return code."""
    return {
        "passed": 1 if rc == 0 else 0,
        "failed": 0 if rc == 0 else 1,
        "errors": 0,
        "failures": [] if rc == 0 else ["Test suite failed (see output)"],
        "raw_output": (stdout + stderr)[-500:],  # Last 500 chars
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


def run_tests(root_dir: str = ".", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Execute detected test frameworks and grade results.

    Returns:
        dict with domain, score, grade, findings, test_results per framework.
    """
    root = Path(root_dir).resolve()
    frameworks = _detect_test_framework(root)

    if not frameworks:
        return {
            "domain": "Test Execution",
            "score": 20,
            "grade": "F",
            "findings": ["No test framework detected — no tests to execute"],
            "justifications": [
                {
                    "criterion": "test_execution",
                    "points": 20,
                    "evidence": str(root),
                    "reasoning": "No recognized test framework (pytest, go test, npm test, "
                    "cargo test, maven, gradle) detected.",
                }
            ],
            "framework_results": [],
            "metrics": {"frameworks_detected": 0},
        }

    framework_results: list[dict] = []
    total_passed = 0
    total_failed = 0
    total_errors = 0
    all_failures: list[str] = []

    for fw in frameworks:
        rc, stdout, stderr = _run_tool(fw["command"], str(root), timeout=timeout)

        if rc == -1:
            framework_results.append(
                {
                    **fw,
                    "status": "tool_not_found",
                    "parsed": {"passed": 0, "failed": 0, "errors": 1, "failures": []},
                }
            )
            total_errors += 1
            continue

        if rc == -2:
            framework_results.append(
                {
                    **fw,
                    "status": "timeout",
                    "parsed": {
                        "passed": 0,
                        "failed": 0,
                        "errors": 1,
                        "failures": [f"Timed out after {timeout}s"],
                    },
                }
            )
            total_errors += 1
            all_failures.append(f"{fw['framework']}: timed out after {timeout}s")
            continue

        # Parse based on framework
        if fw["framework"] == "pytest":
            parsed = _parse_pytest_output(stdout, stderr)
        elif fw["framework"] == "go test":
            parsed = _parse_go_test_output(stdout, stderr)
        else:
            parsed = _parse_generic_output(stdout, stderr, rc)

        framework_results.append(
            {
                **fw,
                "status": "passed" if rc == 0 else "failed",
                "exit_code": rc,
                "parsed": parsed,
            }
        )

        total_passed += parsed.get("passed", 0)
        total_failed += parsed.get("failed", 0)
        total_errors += parsed.get("errors", 0)
        all_failures.extend(parsed.get("failures", []))

    # Scoring
    total_tests = total_passed + total_failed
    score = 100
    findings: list[str] = []

    if total_tests == 0:
        score = 25
        findings.append(
            "No tests were executed (test framework detected but no tests found)"
        )
    else:
        pass_rate = total_passed / total_tests
        if pass_rate < 0.50:
            score -= 40
            findings.append(
                f"Critical: only {pass_rate:.0%} of tests pass ({total_passed}/{total_tests})"
            )
        elif pass_rate < 0.70:
            score -= 25
            findings.append(
                f"Low pass rate: {pass_rate:.0%} ({total_passed}/{total_tests})"
            )
        elif pass_rate < 0.90:
            score -= 10
            findings.append(
                f"Moderate pass rate: {pass_rate:.0%} ({total_passed}/{total_tests})"
            )
        elif pass_rate < 0.95:
            score -= 5

    if total_errors > 0:
        score -= min(15, total_errors * 5)
        findings.append(f"{total_errors} test execution error(s)")

    # Add individual failures as findings (for SDD handoff)
    for failure in all_failures[:20]:
        findings.append(f"FAILED: {failure}")

    score = max(0, score)

    metrics = {
        "frameworks_detected": len(frameworks),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "pass_rate": round(total_passed / max(total_tests, 1), 3),
        "timeout": timeout,
    }

    justifications = [
        {
            "criterion": "test_execution",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"Executed {len(frameworks)} framework(s). "
                f"{total_passed} passed, {total_failed} failed, {total_errors} errors. "
                f"Pass rate: {metrics['pass_rate']:.0%}."
            ),
        }
    ]

    return {
        "domain": "Test Execution",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "framework_results": framework_results,
        "metrics": metrics,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(run_tests(target), indent=2))

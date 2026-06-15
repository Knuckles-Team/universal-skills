#!/usr/bin/env python3
"""FR-009: Linter orchestration for code-enhancer skill.

Runs ruff, bandit, and mypy against a target codebase and parses output
into structured findings with scoring.

CONCEPT:CE-009 — Linting & Formatting Analysis
"""

import json
import subprocess
import sys
from pathlib import Path

# Directories the near-universal lint gate excludes (tests/scripts are validated at
# runtime by the test suite, not statically type/lint-checked). Counting them here
# inflated findings far above what the project's own pre-commit gate enforces.
# (CE-044) Ruff/mypy still read the project's own pyproject config because each tool
# is run with cwd=<root>; these excludes only align the *file set* with the gate.
_GATE_EXCLUDE_DIRS = ("tests", "test", "scripts", "script")
# The standard bandit skip-set used across the fleet's pre-commit gates (assert in
# tests, bind-all, hardcoded-tmp, try-except-pass, subprocess import/with-shell-false…).
_BANDIT_SKIP = "B101,B104,B105,B110,B404,B603,B607,B608"


def _mypy_exclude_regex() -> str:
    """A single regex matching the gate-excluded dirs for ``mypy --exclude``."""
    return r"(^|/)(" + "|".join(_GATE_EXCLUDE_DIRS) + r")/"


def _run_tool(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a CLI tool and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", f"Tool timed out: {' '.join(cmd)}"


def _parse_ruff_output(stdout: str) -> list[dict]:
    """Parse ruff check output lines into structured findings."""
    findings = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("Found") or line.startswith("All checks"):
            continue
        # Format: path/file.py:line:col: CODE message
        parts = line.split(":", 3)
        if len(parts) >= 4:
            findings.append(
                {
                    "file": parts[0].strip(),
                    "line": parts[1].strip(),
                    "col": parts[2].strip(),
                    "message": parts[3].strip(),
                    "tool": "ruff",
                }
            )
    return findings


def _parse_bandit_output(stdout: str) -> list[dict]:
    """Parse bandit text output into structured findings."""
    findings = []
    current: dict = {}
    for line in stdout.splitlines():
        if line.startswith(">> Issue:"):
            if current:
                findings.append(current)
            msg = line.replace(">> Issue:", "").strip()
            current = {"message": msg, "tool": "bandit", "severity": "Medium"}
        elif line.strip().startswith("Severity:"):
            parts = line.strip().split()
            if len(parts) >= 2:
                current["severity"] = parts[1]
        elif line.strip().startswith("Location:"):
            loc = line.strip().replace("Location:", "").strip()
            loc_parts = loc.split(":")
            if len(loc_parts) >= 2:
                current["file"] = loc_parts[0]
                current["line"] = loc_parts[1]
        elif line.strip().startswith("CWE:"):
            current["cwe"] = line.strip().split("(")[0].replace("CWE:", "").strip()
    if current:
        findings.append(current)
    return findings


def _parse_mypy_output(stdout: str) -> list[dict]:
    """Parse mypy output into structured findings."""
    findings = []
    for line in stdout.strip().splitlines():
        if ": error:" in line or ": warning:" in line or ": note:" in line:
            parts = line.split(":", 3)
            if len(parts) >= 4:
                severity = "error" if "error" in parts[2] else "warning"
                findings.append(
                    {
                        "file": parts[0].strip(),
                        "line": parts[1].strip(),
                        "message": parts[3].strip(),
                        "severity": severity,
                        "tool": "mypy",
                    }
                )
    return findings


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


def run_linters(root_dir: str = ".") -> dict:
    """Run ruff, bandit, and mypy against the target and score results.

    Returns:
        dict with domain, score, grade, findings, justifications, tool_results
    """
    root = Path(root_dir).resolve()
    all_findings: list[dict] = []
    tool_results: dict[str, dict] = {}

    # --- Ruff --- (reads the project's [tool.ruff] config via cwd=root)
    rc, stdout, stderr = _run_tool(
        [
            "ruff",
            "check",
            "--ignore=E402",
            "--exclude",
            ",".join(_GATE_EXCLUDE_DIRS),
            str(root),
        ],
        str(root),
    )
    ruff_findings = _parse_ruff_output(stdout) if rc != -1 else []
    tool_results["ruff"] = {
        "available": rc != -1,
        "finding_count": len(ruff_findings),
        "returncode": rc,
    }
    all_findings.extend(ruff_findings)

    # --- Bandit --- (honors inline ``# nosec`` natively; skip-set + test/script
    # excludes match the fleet's pre-commit gate)
    rc, stdout, stderr = _run_tool(
        [
            "bandit",
            "-r",
            "--skip",
            _BANDIT_SKIP,
            "-x",
            ",".join(f"*/{d}/*" for d in _GATE_EXCLUDE_DIRS),
            str(root),
        ],
        str(root),
    )
    bandit_findings = _parse_bandit_output(stdout) if rc != -1 else []
    tool_results["bandit"] = {
        "available": rc != -1,
        "finding_count": len(bandit_findings),
        "returncode": rc,
    }
    all_findings.extend(bandit_findings)

    # --- Mypy --- (reads [tool.mypy] via cwd=root; excludes test/script dirs the
    # gate does not type-check)
    rc, stdout, stderr = _run_tool(
        [
            "mypy",
            "--ignore-missing-imports",
            "--follow-imports=silent",
            "--exclude",
            _mypy_exclude_regex(),
            str(root),
        ],
        str(root),
    )
    mypy_findings = _parse_mypy_output(stdout + stderr) if rc != -1 else []
    tool_results["mypy"] = {
        "available": rc != -1,
        "finding_count": len(mypy_findings),
        "returncode": rc,
    }
    all_findings.extend(mypy_findings)

    # --- Scoring ---
    score = 100
    high_count = 0
    med_count = 0
    low_count = 0
    for f in all_findings:
        sev = f.get("severity", "Low")
        if sev in ("High", "error"):
            score -= 5
            high_count += 1
        elif sev in ("Medium", "warning"):
            score -= 2
            med_count += 1
        else:
            score -= 1
            low_count += 1
    score = max(0, score)

    findings_summary = [
        f"Total lint findings: {len(all_findings)} "
        f"(high/error: {high_count}, medium/warning: {med_count}, low: {low_count})",
    ]
    for tool_name, info in tool_results.items():
        if not info["available"]:
            findings_summary.append(f"{tool_name}: not available in PATH")

    justifications = [
        {
            "criterion": "lint_compliance",
            "points": score,
            "evidence": f"ruff={tool_results['ruff']['finding_count']}, "
            f"bandit={tool_results['bandit']['finding_count']}, "
            f"mypy={tool_results['mypy']['finding_count']}",
            "reasoning": f"{len(all_findings)} total findings across 3 tools. "
            f"High/error: -{high_count * 5}pts, Med/warning: -{med_count * 2}pts, "
            f"Low: -{low_count}pt.",
        }
    ]

    return {
        "domain": "Linting & Formatting",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings_summary,
        "justifications": justifications,
        "tool_results": tool_results,
        "all_findings": all_findings[:50],  # Cap at 50 for report size
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(run_linters(target), indent=2))

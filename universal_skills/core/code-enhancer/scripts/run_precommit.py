#!/usr/bin/env python3
"""CE-015: Pre-commit compliance analysis for code-enhancer skill.

Runs ``pre-commit run --all-files`` and detects outdated hooks by parsing
the ``.pre-commit-config.yaml`` rev fields against upstream tags.

Smart pytest deduplication: if pre-commit config contains a pytest hook,
it is **skipped** here to avoid double-execution — CE-016 (Test Execution)
handles test running with richer per-test analysis.

CONCEPT:CE-015 — Pre-Commit Compliance
"""

import json
import re
import subprocess
import sys
from pathlib import Path

_PYTEST_HOOK_IDS = frozenset(
    {
        "pytest",
        "pytest-check",
        "python-pytest",
        "tests",
        "pytest-cov",
        "local-pytest",
        "system-pytest",
    }
)


def _find_precommit_config(root: Path) -> Path | None:
    """Locate .pre-commit-config.yaml or .yml variant."""
    for name in (".pre-commit-config.yaml", ".pre-commit-config.yml"):
        p = root / name
        if p.exists():
            return p
    return None


def _parse_hook_results(stdout: str, stderr: str) -> list[dict]:
    """Parse pre-commit run output into per-hook results."""
    hooks: list[dict] = []
    # Output format: "hookid....................................Passed/Failed/Skipped"
    pattern = re.compile(r"^(.+?)\.{3,}\s*(Passed|Failed|Skipped)$", re.MULTILINE)
    for match in pattern.finditer(stdout + "\n" + stderr):
        hook_name = match.group(1).strip()
        status = match.group(2).strip().lower()
        hooks.append({"hook": hook_name, "status": status})

    # Also capture hooks that produce output without the dots pattern
    # (e.g., hooks that fail with multi-line output)
    if not hooks:
        # Fallback: parse line-by-line for common patterns
        for line in (stdout + "\n" + stderr).splitlines():
            line = line.strip()
            if (
                line.endswith("Passed")
                or line.endswith("Failed")
                or line.endswith("Skipped")
            ):
                parts = line.rsplit(None, 1)
                if len(parts) == 2:
                    hooks.append(
                        {
                            "hook": parts[0].strip().rstrip("."),
                            "status": parts[1].lower(),
                        }
                    )
    return hooks


def _detect_pytest_hooks_in_config(config_path: Path) -> list[str]:
    """Detect pytest-related hook IDs in the pre-commit config.

    Returns list of hook IDs that should be skipped (CE-016 handles them).
    """
    try:
        content = config_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    pytest_hooks: list[str] = []
    # Simple YAML parsing — look for id: lines under hooks:
    in_hooks = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            hook_id = stripped.split(":", 1)[1].strip()
            in_hooks = True
        elif stripped.startswith("id:"):
            hook_id = stripped.split(":", 1)[1].strip()
        else:
            continue

        # Check against known pytest hook IDs
        hook_id_lower = hook_id.lower()
        if any(pid in hook_id_lower for pid in _PYTEST_HOOK_IDS):
            pytest_hooks.append(hook_id)
        # Also check for generic "pytest" in entry/args (common in local hooks)
        # We'll catch these via the hook name matching below

    # Also scan for entry: pytest or args: [pytest] patterns
    if "pytest" in content.lower():
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("entry:") and "pytest" in stripped.lower():
                # Find the parent hook id
                pytest_hooks.append("local-pytest")
                break

    return list(set(pytest_hooks))


def _detect_outdated_hooks(config_path: Path) -> list[dict]:
    """Detect outdated hooks by comparing rev values against upstream.

    Since ``pre-commit autoupdate`` has no ``--dry-run`` flag, we parse
    the config and check if any rev values use commit hashes instead of
    tags (which suggests they may be outdated or pinned).

    For a lightweight check, we also look for obviously old version patterns.
    """
    outdated: list[dict] = []
    try:
        content = config_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return outdated

    # Parse repo/rev pairs
    current_repo = ""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- repo:"):
            current_repo = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("repo:"):
            current_repo = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("rev:"):
            rev = stripped.split(":", 1)[1].strip().strip("'\"")
            if current_repo and rev:
                # Check for commit hash (40 char hex) — suggests pinned/outdated
                if re.match(r"^[0-9a-f]{40}$", rev):
                    outdated.append(
                        {
                            "repo": current_repo,
                            "current_rev": rev[:12] + "...",
                            "issue": "Pinned to commit hash — may be outdated",
                        }
                    )
                # Check for very old version patterns (v0.x, v1.x when v2+ common)
                elif re.match(r"^v?0\.\d+", rev):
                    outdated.append(
                        {
                            "repo": current_repo,
                            "current_rev": rev,
                            "issue": "Pre-1.0 version — check for updates",
                        }
                    )

    return outdated


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


def run_precommit(root_dir: str = ".") -> dict:
    """Run pre-commit checks and produce scored results.

    Smart deduplication: pytest hooks are skipped — CE-016 handles test
    execution with richer analysis.

    Returns:
        dict with domain, score, grade, findings, justifications, hook_results.
    """
    root = Path(root_dir).resolve()
    config_path = _find_precommit_config(root)

    if config_path is None:
        return {
            "domain": "Pre-Commit Compliance",
            "score": 15,
            "grade": "F",
            "findings": [
                "No .pre-commit-config.yaml found — "
                "pre-commit hooks are not configured for this project"
            ],
            "justifications": [
                {
                    "criterion": "precommit_config",
                    "points": 15,
                    "evidence": str(root),
                    "reasoning": "No pre-commit configuration file detected. "
                    "Automated code quality checks on commit are absent.",
                }
            ],
            "hook_results": [],
            "pytest_hooks_skipped": [],
            "outdated_hooks": [],
        }

    # Detect pytest hooks to skip
    pytest_hooks = _detect_pytest_hooks_in_config(config_path)
    skip_env = {}
    if pytest_hooks:
        skip_env["SKIP"] = ",".join(pytest_hooks)

    # Run pre-commit
    env = {**__import__("os").environ, **skip_env}
    try:
        result = subprocess.run(
            ["pre-commit", "run", "--all-files"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=300,
            env=env,
        )
        rc = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except FileNotFoundError:
        return {
            "domain": "Pre-Commit Compliance",
            "score": 30,
            "grade": "F",
            "findings": ["pre-commit is not installed or not in PATH"],
            "justifications": [
                {
                    "criterion": "precommit_available",
                    "points": 30,
                    "evidence": "which pre-commit",
                    "reasoning": "pre-commit binary not found — cannot run checks.",
                }
            ],
            "hook_results": [],
            "pytest_hooks_skipped": pytest_hooks,
            "outdated_hooks": [],
        }
    except subprocess.TimeoutExpired:
        return {
            "domain": "Pre-Commit Compliance",
            "score": 40,
            "grade": "F",
            "findings": ["pre-commit run timed out after 300 seconds"],
            "justifications": [
                {
                    "criterion": "precommit_timeout",
                    "points": 40,
                    "evidence": "timeout=300s",
                    "reasoning": "Pre-commit execution exceeded 300s timeout.",
                }
            ],
            "hook_results": [],
            "pytest_hooks_skipped": pytest_hooks,
            "outdated_hooks": [],
        }

    # Parse hook results
    hook_results = _parse_hook_results(stdout, stderr)

    # Detect outdated hooks
    outdated = _detect_outdated_hooks(config_path)

    # Scoring
    score = 100
    findings: list[str] = []

    passed = sum(1 for h in hook_results if h["status"] == "passed")
    failed = sum(1 for h in hook_results if h["status"] == "failed")
    skipped = sum(1 for h in hook_results if h["status"] == "skipped")
    total = len(hook_results)

    if failed > 0:
        penalty = min(50, failed * 5)
        score -= penalty
        failed_names = [h["hook"] for h in hook_results if h["status"] == "failed"]
        findings.append(
            f"{failed}/{total} pre-commit hooks failed: " + ", ".join(failed_names[:10])
        )

    if outdated:
        penalty = min(15, len(outdated) * 3)
        score -= penalty
        findings.append(
            f"{len(outdated)} hook(s) may be outdated: "
            + ", ".join(h["repo"].split("/")[-1] for h in outdated[:5])
        )

    if pytest_hooks:
        findings.append(
            "Pytest hooks skipped (handled by CE-016 Test Execution): "
            + ", ".join(pytest_hooks)
        )

    if total == 0 and rc != 0:
        score -= 20
        findings.append("Pre-commit ran but produced no parseable hook results")
        # Include raw output for debugging
        if stderr.strip():
            findings.append(f"stderr: {stderr.strip()[:200]}")

    score = max(0, score)

    metrics = {
        "total_hooks": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "outdated_hooks": len(outdated),
        "pytest_hooks_skipped": len(pytest_hooks),
        "exit_code": rc,
    }

    justifications = [
        {
            "criterion": "precommit_compliance",
            "points": score,
            "evidence": json.dumps(metrics),
            "reasoning": (
                f"Ran pre-commit with {total} hooks: "
                f"{passed} passed, {failed} failed, {skipped} skipped. "
                f"{len(outdated)} potentially outdated. "
                f"{len(pytest_hooks)} pytest hooks deferred to CE-016."
            ),
        }
    ]

    return {
        "domain": "Pre-Commit Compliance",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "hook_results": hook_results,
        "pytest_hooks_skipped": pytest_hooks,
        "outdated_hooks": outdated,
        "metrics": metrics,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(run_precommit(target), indent=2))

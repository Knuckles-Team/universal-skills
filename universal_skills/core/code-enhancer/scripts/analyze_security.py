#!/usr/bin/env python3
"""FR-004, FR-010: Security analysis for code-enhancer skill.

Discovers attack surface, scans for CWE patterns, parses bandit/pip-audit
output, and consolidates into a scored vulnerability register.

CONCEPT:CE-004 — Security & Vulnerability Analysis
"""

import ast
import json
import subprocess
import sys
from pathlib import Path


# CWE patterns detectable via AST
CWE_PATTERNS = {
    "CWE-78": {
        "name": "OS Command Injection",
        "ast_calls": ["os.system", "subprocess.call", "subprocess.Popen", "subprocess.run"],
        "severity": "High",
    },
    "CWE-94": {
        "name": "Code Injection",
        "ast_calls": ["eval", "exec", "compile"],
        "severity": "High",
    },
    "CWE-327": {
        "name": "Broken Crypto",
        "ast_imports": ["md5", "sha1"],
        "severity": "Medium",
    },
    "CWE-502": {
        "name": "Deserialization",
        "ast_calls": ["pickle.loads", "pickle.load", "yaml.load"],
        "severity": "High",
    },
    "CWE-676": {
        "name": "Dangerous Function",
        "ast_calls": ["__import__"],
        "severity": "Medium",
    },
    "CWE-798": {
        "name": "Hardcoded Credentials",
        "ast_patterns": ["password", "secret", "api_key", "token"],
        "severity": "High",
    },
}


# Identifier-name suffixes that denote a NON-secret (id, count, budget, label…).
_NONSECRET_NAME_SUFFIXES = (
    "_id",
    "_ids",
    "_name",
    "_names",
    "_max",
    "_min",
    "_budget",
    "_count",
    "_tokens",
    "_ttl",
    "_type",
    "_field",
    "_var",
    "_env",
    "_path",
    "_url",
    "_prefix",
    "_header",
    "_engine_id",
    "_level",
    "_mode",
)
# Value words that are placeholders / enum labels, never real secrets.
_PLACEHOLDER_VALUES = frozenset(
    {
        "secret",
        "top_secret",
        "top secret",
        "confidential",
        "unclassified",
        "classified",
        "public",
        "private",
        "password",
        "changeme",
        "change_me",
        "example",
        "dummy",
        "test",
        "none",
        "null",
        "redacted",
        "xxxxxxxx",
        "your_token_here",
        "your_secret_here",
    }
)


def _looks_like_real_secret(name: str, value: str) -> bool:
    """Gate CWE-798 on the VALUE shape, not just the variable name.

    Real hardcoded credentials are opaque high-entropy strings. We exclude:
      - non-secret identifier names (``*_id``, ``*_max``, ``*_count``, …),
      - placeholder / enum-label values (``SECRET``, ``TOP_SECRET``, ``changeme``),
      - plain ``snake_case``/dotted config identifiers (e.g. ``secret_engine_id``),
      - short values (< 8 chars).
    This removes the dominant false-positive class (a constant *named* like a
    secret but holding a label, budget, or config key).
    """
    name_l = name.lower()
    if name_l.endswith(_NONSECRET_NAME_SUFFIXES):
        return False
    if not isinstance(value, str) or len(value) < 8:
        return False
    if value.strip().lower() in _PLACEHOLDER_VALUES:
        return False
    # All-lowercase snake_case / dotted / slug → a config identifier, not a secret.
    import re as _re

    if _re.fullmatch(r"[a-z0-9_.\-/]+", value) and not _re.search(r"\d{3,}", value):
        return False
    return True


# CWE classes that are routinely intentional inside test fixtures.
_TEST_SUPPRESSED_CWES = frozenset({"CWE-78", "CWE-94", "CWE-502", "CWE-798"})


def _scan_file_for_patterns(filepath: Path) -> list[dict]:
    """Scan a Python file for CWE-related patterns using AST."""
    findings: list[dict] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return findings

    is_test_file = "tests" in filepath.parts or filepath.name.startswith("test_")

    for node in ast.walk(tree):
        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            call_name = ""
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    call_name = f"{node.func.value.id}.{node.func.attr}"

            for cwe_id, pattern in CWE_PATTERNS.items():
                # Suppress intentional-in-tests CWE classes (subprocess/eval/exec/
                # pickle in fixtures) to avoid noise from the test suite.
                if cwe_id in _TEST_SUPPRESSED_CWES and is_test_file:
                    continue

                if call_name in pattern.get("ast_calls", []):
                    severity = pattern["severity"]
                    # subprocess.* without shell=True is bandit-Low/Medium, not
                    # High — only a shell invocation is true command injection.
                    if cwe_id == "CWE-78" and call_name.startswith("subprocess."):
                        shell_true = any(
                            kw.arg == "shell"
                            and isinstance(kw.value, ast.Constant)
                            and kw.value.value is True
                            for kw in node.keywords
                        )
                        severity = "High" if shell_true else "Medium"
                    findings.append(
                        {
                            "cwe": cwe_id,
                            "name": pattern["name"],
                            "severity": severity,
                            "file": str(filepath),
                            "line": node.lineno,
                            "detail": f"Dangerous call: {call_name}()",
                        }
                    )

        # Check for hardcoded credential patterns in assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name_lower = target.id.lower()
                    for keyword in CWE_PATTERNS.get("CWE-798", {}).get(
                        "ast_patterns", []
                    ):
                        if keyword in name_lower and isinstance(
                            node.value, ast.Constant
                        ):
                            # Suppress CWE-798 for test files (dummy secrets are common)
                            if is_test_file:
                                continue
                            # Gate on the VALUE shape, not just the name — removes
                            # the dominant FP class (label/budget/config-id constants).
                            if _looks_like_real_secret(target.id, node.value.value):
                                findings.append(
                                    {
                                        "cwe": "CWE-798",
                                        "name": "Hardcoded Credentials",
                                        "severity": "High",
                                        "file": str(filepath),
                                        "line": node.lineno,
                                        "detail": f"Possible hardcoded credential in '{target.id}'",
                                    }
                                )

    return findings


def _count_attack_surface(root: Path, py_files: list[Path]) -> dict:
    """Count attack surface indicators."""
    surface = {
        "subprocess_calls": 0,
        "file_io_calls": 0,
        "network_endpoints": 0,
        "eval_exec_usage": 0,
        "sql_usage": 0,
    }
    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        surface["subprocess_calls"] += source.count("subprocess.")
        surface["file_io_calls"] += source.count("open(") + source.count("Path(")
        surface["network_endpoints"] += source.count("@app.") + source.count("@router.")
        import re

        surface["eval_exec_usage"] += len(
            re.findall(r"(?<!\.)\b(?:eval|exec)\s*\(", source)
        )
        surface["sql_usage"] += source.lower().count("execute(") + source.lower().count(
            "cursor."
        )
    return surface


def _run_pip_audit(root_dir: str) -> list[dict]:
    """Run pip-audit and parse JSON output if available."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json", "--desc"],
            capture_output=True,
            text=True,
            cwd=root_dir,
            timeout=120,
        )
        if result.returncode in (0, 1) and result.stdout.strip():
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


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


def analyze_security(root_dir: str = ".", *, filter_fp: bool = True) -> dict:
    """Analyze security posture and produce scored results.

    When ``filter_fp`` (default), the consolidated register is passed through the
    deterministic false-positive filter (CE-041) to drop the noisy classes
    (generic DOS/rate-limit advice, resource leaks, non-C memory-safety, etc.)
    before scoring, so the grade reflects real findings.
    """
    root = Path(root_dir).resolve()
    py_files = [
        f
        for f in root.rglob("*.py")
        if ".venv" not in f.parts
        and "__pycache__" not in f.parts
        and "node_modules" not in f.parts
        and ".git" not in f.parts
        and "target" not in f.parts
    ]

    if not py_files:
        return {
            "domain": "Security Analysis",
            "score": 0,
            "grade": "F",
            "findings": ["No Python files found"],
            "justifications": [],
            "vulnerabilities": [],
            "attack_surface": {},
        }

    # AST-based CWE scanning
    all_vulns: list[dict] = []
    for f in py_files:
        all_vulns.extend(_scan_file_for_patterns(f))

    # Attack surface
    attack_surface = _count_attack_surface(root, py_files)

    # pip-audit
    pip_audit_results = _run_pip_audit(root_dir)
    for vuln in pip_audit_results:
        if isinstance(vuln, dict):
            all_vulns.append(
                {
                    "cwe": vuln.get("id", "CVE-Unknown"),
                    "name": vuln.get("name", "Unknown"),
                    "severity": "High",
                    "file": "dependency",
                    "line": 0,
                    "detail": vuln.get("description", ""),
                }
            )

    # CE-041: drop likely false positives before scoring (deterministic, no network).
    fp_excluded: list[dict] = []
    if filter_fp and all_vulns:
        try:
            from findings_filter import filter_findings  # local module

            all_vulns, fp_excluded, _ = filter_findings(all_vulns)
        except ImportError:
            pass  # filter optional; fall back to the raw register

    # Scoring
    score = 100
    high_count = sum(1 for v in all_vulns if v.get("severity") == "High")
    med_count = sum(1 for v in all_vulns if v.get("severity") == "Medium")
    low_count = sum(1 for v in all_vulns if v.get("severity") == "Low")

    # HIGH findings are serious and (after FP filtering) rare — keep per-finding.
    # MEDIUM/LOW are dominated by "dangerous function" noise that scales with repo
    # size; cap their contribution so a large mature codebase is graded on real
    # high-severity exposure, not raw count (which previously floored every big
    # repo to 0). See references/evolution_log.md (security density tuning).
    score -= high_count * 15
    score -= min(med_count * 8, 40)
    score -= min(low_count * 3, 15)
    # NOTE: eval/exec and subprocess are already scored per-finding above
    # (CWE-94 / CWE-78); the attack_surface counters are reported as evidence
    # only (no second deduction) to avoid double-penalising the same call.

    score = max(0, score)
    findings: list[str] = []
    if high_count:
        findings.append(f"{high_count} HIGH severity vulnerabilities found")
    if med_count:
        findings.append(f"{med_count} MEDIUM severity vulnerabilities found")
    if attack_surface["eval_exec_usage"] > 0:
        findings.append(
            f"eval/exec usage detected: {attack_surface['eval_exec_usage']} instances"
        )

    justifications = [
        {
            "criterion": "security_posture",
            "points": score,
            "evidence": f"high={high_count} med={med_count} low={low_count} "
            f"attack_surface={json.dumps(attack_surface)}",
            "reasoning": (
                f"Scanned {len(py_files)} files. Found {len(all_vulns)} security findings. "
                f"High: -{high_count * 15}pts, Med: -{med_count * 8}pts, Low: -{low_count * 3}pts."
            ),
        }
    ]

    return {
        "domain": "Security Analysis",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "vulnerabilities": all_vulns[:50],
        "filtered_false_positives": len(fp_excluded),
        "attack_surface": attack_surface,
    }


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--no-filter"]
    target = args[0] if args else "."
    print(
        json.dumps(
            analyze_security(target, filter_fp="--no-filter" not in sys.argv), indent=2
        )
    )

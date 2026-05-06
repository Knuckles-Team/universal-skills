#!/usr/bin/env python3
"""CA-005: Security analysis — OWASP, CWE patterns, secrets, auth.

Usage: python analyze_security.py /path/to/project

CONCEPT:CA-005 — Security & Compliance
"""

import ast
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"}

DANGEROUS_PATTERNS = [
    {"name": "eval_usage", "pattern": re.compile(r"\beval\s*\("), "severity": "critical", "cwe": "CWE-95", "penalty": -15},
    {"name": "exec_usage", "pattern": re.compile(r"\bexec\s*\("), "severity": "critical", "cwe": "CWE-95", "penalty": -15},
    {"name": "shell_true", "pattern": re.compile(r"shell\s*=\s*True"), "severity": "high", "cwe": "CWE-78", "penalty": -10},
    {"name": "os_system", "pattern": re.compile(r"os\.system\s*\("), "severity": "high", "cwe": "CWE-78", "penalty": -10},
    {"name": "pickle_loads", "pattern": re.compile(r"pickle\.loads?\s*\("), "severity": "high", "cwe": "CWE-502", "penalty": -10},
    {"name": "yaml_load", "pattern": re.compile(r"yaml\.load\s*\((?!.*Loader)"), "severity": "medium", "cwe": "CWE-502", "penalty": -5},
    {"name": "assert_validation", "pattern": re.compile(r"^\s*assert\s+"), "severity": "low", "cwe": "CWE-617", "penalty": -3},
    {"name": "debug_true", "pattern": re.compile(r"DEBUG\s*=\s*True"), "severity": "medium", "cwe": "CWE-489", "penalty": -5},
    {"name": "wildcard_cors", "pattern": re.compile(r'allow_origins\s*=\s*\[?\s*["\']?\*'), "severity": "medium", "cwe": "CWE-942", "penalty": -5},
]

SECRET_PATTERNS = [
    re.compile(r'(?:password|passwd|pwd|secret|token|api_key|apikey)\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    re.compile(r'(?:sk-|ghp_|glpat-|xoxb-|AKIA)[A-Za-z0-9]{10,}'),
]


def scan_security(project_path: Path) -> dict:
    """Scan for security anti-patterns."""
    findings = []
    secret_findings = []
    file_count = 0

    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        if "test" in str(rel).lower():
            continue
        file_count += 1
        try:
            content = f.read_text(errors="ignore")
            for i, line in enumerate(content.split("\n"), 1):
                for pat in DANGEROUS_PATTERNS:
                    if pat["pattern"].search(line):
                        findings.append({
                            "file": str(rel), "line": i,
                            "name": pat["name"], "severity": pat["severity"],
                            "cwe": pat["cwe"],
                        })
                for sp in SECRET_PATTERNS:
                    if sp.search(line):
                        secret_findings.append({"file": str(rel), "line": i})
        except (OSError, UnicodeDecodeError):
            pass

    return {
        "files_scanned": file_count,
        "findings": findings[:50],
        "finding_count": len(findings),
        "secrets_detected": len(secret_findings),
    }


def check_security_posture(project_path: Path) -> dict:
    """Check for positive security indicators."""
    posture = {
        "security_md": any((project_path / f).exists() for f in ["SECURITY.md", ".github/SECURITY.md"]),
        "input_validation": False,
        "auth_framework": False,
        "security_linter": False,
        "dep_scanning": False,
    }

    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = f.read_text(errors="ignore")
            if "pydantic" in content and "BaseModel" in content:
                posture["input_validation"] = True
            if any(kw in content for kw in ["JWT", "OAuth", "jwt_required", "Depends(", "HTTPBearer"]):
                posture["auth_framework"] = True
        except (OSError, UnicodeDecodeError):
            pass

    # Check pre-commit for security tools
    for cfg in [".pre-commit-config.yaml", "pyproject.toml"]:
        p = project_path / cfg
        if p.exists():
            try:
                content = p.read_text(errors="ignore")
                if "bandit" in content or "semgrep" in content:
                    posture["security_linter"] = True
                if "pip-audit" in content or "safety" in content:
                    posture["dep_scanning"] = True
            except Exception:
                pass

    return posture


def score_security(scan: dict, posture: dict) -> dict:
    """Calculate 0-100 security score."""
    score = 100
    details = []

    # Deduct for findings
    findings = scan.get("finding_count", 0)
    secrets = scan.get("secrets_detected", 0)

    if secrets > 0:
        score -= min(secrets * 20, 40)
        details.append(f"Hardcoded secrets detected ({secrets}): -{min(secrets * 20, 40)}")
    if findings > 20:
        score -= 30
        details.append(f"Many security findings ({findings}): -30")
    elif findings > 10:
        score -= 20
        details.append(f"Moderate findings ({findings}): -20")
    elif findings > 5:
        score -= 10
        details.append(f"Some findings ({findings}): -10")

    # Bonuses for positive posture
    if posture.get("security_md"):
        score += 5
        details.append("SECURITY.md present: +5")
    if posture.get("input_validation"):
        score += 5
        details.append("Input validation (Pydantic): +5")
    if posture.get("auth_framework"):
        score += 5
        details.append("Auth framework detected: +5")
    if posture.get("security_linter"):
        score += 5
        details.append("Security linter in pipeline: +5")

    score = max(min(score, 100), 0)
    grade = "A+" if score >= 95 else "A" if score >= 90 else "B+" if score >= 85 else "B" if score >= 80 else "C+" if score >= 75 else "C" if score >= 70 else "D" if score >= 60 else "F"
    return {"score": score, "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_security.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    scan = scan_security(project_path)
    posture = check_security_posture(project_path)
    scoring = score_security(scan, posture)

    print(json.dumps({
        "domain": "CA-005", "domain_name": "Security",
        "project": str(project_path),
        "scan_results": scan, "security_posture": posture, "scoring": scoring,
    }, indent=2))


if __name__ == "__main__":
    main()

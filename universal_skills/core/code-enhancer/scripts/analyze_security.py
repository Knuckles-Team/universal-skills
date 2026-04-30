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
    "CWE-78": {"name": "OS Command Injection", "ast_calls": ["os.system", "subprocess.call", "subprocess.Popen"],
               "severity": "High"},
    "CWE-94": {"name": "Code Injection", "ast_calls": ["eval", "exec", "compile"],
               "severity": "High"},
    "CWE-327": {"name": "Broken Crypto", "ast_imports": ["md5", "sha1"],
                "severity": "Medium"},
    "CWE-502": {"name": "Deserialization", "ast_calls": ["pickle.loads", "pickle.load", "yaml.load"],
                "severity": "High"},
    "CWE-676": {"name": "Dangerous Function", "ast_calls": ["__import__"],
                "severity": "Medium"},
    "CWE-798": {"name": "Hardcoded Credentials", "ast_patterns": ["password", "secret", "api_key", "token"],
                "severity": "High"},
}


def _scan_file_for_patterns(filepath: Path) -> list[dict]:
    """Scan a Python file for CWE-related patterns using AST."""
    findings: list[dict] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return findings

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
                if call_name in pattern.get("ast_calls", []):
                    findings.append({
                        "cwe": cwe_id, "name": pattern["name"],
                        "severity": pattern["severity"],
                        "file": str(filepath), "line": node.lineno,
                        "detail": f"Dangerous call: {call_name}()",
                    })

        # Check for hardcoded credential patterns in assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name_lower = target.id.lower()
                    for keyword in CWE_PATTERNS.get("CWE-798", {}).get("ast_patterns", []):
                        if keyword in name_lower and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, str) and len(node.value.value) > 3:
                                findings.append({
                                    "cwe": "CWE-798", "name": "Hardcoded Credentials",
                                    "severity": "High",
                                    "file": str(filepath), "line": node.lineno,
                                    "detail": f"Possible hardcoded credential in '{target.id}'",
                                })

    return findings


def _count_attack_surface(root: Path, py_files: list[Path]) -> dict:
    """Count attack surface indicators."""
    surface = {
        "subprocess_calls": 0, "file_io_calls": 0, "network_endpoints": 0,
        "eval_exec_usage": 0, "sql_usage": 0,
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
        surface["eval_exec_usage"] += len(re.findall(r"(?<!\.)\b(?:eval|exec)\s*\(", source))
        surface["sql_usage"] += source.lower().count("execute(") + source.lower().count("cursor.")
    return surface


def _run_pip_audit(root_dir: str) -> list[dict]:
    """Run pip-audit and parse JSON output if available."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json", "--desc"],
            capture_output=True, text=True, cwd=root_dir, timeout=120,
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


def analyze_security(root_dir: str = ".") -> dict:
    """Analyze security posture and produce scored results."""
    root = Path(root_dir).resolve()
    py_files = [f for f in root.rglob("*.py")
                if ".venv" not in f.parts and "__pycache__" not in f.parts
                and "node_modules" not in f.parts and ".git" not in f.parts]

    if not py_files:
        return {"domain": "Security Analysis", "score": 0, "grade": "F",
                "findings": ["No Python files found"], "justifications": [],
                "vulnerabilities": [], "attack_surface": {}}

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
            all_vulns.append({
                "cwe": vuln.get("id", "CVE-Unknown"),
                "name": vuln.get("name", "Unknown"),
                "severity": "High",
                "file": "dependency",
                "line": 0,
                "detail": vuln.get("description", ""),
            })

    # Scoring
    score = 100
    high_count = sum(1 for v in all_vulns if v.get("severity") == "High")
    med_count = sum(1 for v in all_vulns if v.get("severity") == "Medium")
    low_count = sum(1 for v in all_vulns if v.get("severity") == "Low")

    score -= high_count * 15
    score -= med_count * 8
    score -= low_count * 3
    # Attack surface penalties
    if attack_surface["eval_exec_usage"] > 0:
        score -= 10
    if attack_surface["subprocess_calls"] > 20:
        score -= 5

    score = max(0, score)
    findings: list[str] = []
    if high_count:
        findings.append(f"{high_count} HIGH severity vulnerabilities found")
    if med_count:
        findings.append(f"{med_count} MEDIUM severity vulnerabilities found")
    if attack_surface["eval_exec_usage"] > 0:
        findings.append(f"eval/exec usage detected: {attack_surface['eval_exec_usage']} instances")

    justifications = [{
        "criterion": "security_posture",
        "points": score,
        "evidence": f"high={high_count} med={med_count} low={low_count} "
                    f"attack_surface={json.dumps(attack_surface)}",
        "reasoning": (f"Scanned {len(py_files)} files. Found {len(all_vulns)} security findings. "
                      f"High: -{high_count * 15}pts, Med: -{med_count * 8}pts, Low: -{low_count * 3}pts."),
    }]

    return {
        "domain": "Security Analysis", "score": score, "grade": _score_to_grade(score),
        "findings": findings, "justifications": justifications,
        "vulnerabilities": all_vulns[:50], "attack_surface": attack_surface,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_security(target), indent=2))

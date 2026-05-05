#!/usr/bin/env python3
"""CE-027: Engineering Heuristics evaluation for code-enhancer skill.

Evaluates a codebase against battle-tested principles synthesized from 13
industry-standard software engineering books (agent-rules-books project).

Uses contextual activation: heuristic categories only score when relevant
patterns are detected in the project.

CONCEPT:CE-027 — Engineering Heuristics
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Heuristic Categories — contextually activated
# ---------------------------------------------------------------------------

HEURISTIC_CATEGORIES = {
    "H1": {
        "name": "Construction Quality",
        "sources": ["Clean Code (Martin)", "Code Complete (McConnell)"],
        "weight": 20,
        "always_active": True,
    },
    "H2": {
        "name": "Architecture Boundaries",
        "sources": ["Clean Architecture (Martin)", "A Philosophy of Software Design (Ousterhout)"],
        "weight": 15,
        "always_active": False,
        "activation": "project has >5 modules or architecture directories",
    },
    "H3": {
        "name": "Refactoring Discipline",
        "sources": ["Refactoring (Fowler)", "Working Effectively with Legacy Code (Feathers)"],
        "weight": 10,
        "always_active": True,
    },
    "H4": {
        "name": "Domain Modeling",
        "sources": ["DDD (Evans)", "DDD Distilled (Vernon)", "Implementing DDD (Vernon)"],
        "weight": 10,
        "always_active": False,
        "activation": "DDD patterns detected (domain/, entities/, aggregates/)",
    },
    "H5": {
        "name": "Production Resilience",
        "sources": ["Release It! (Nygard)", "DDIA (Kleppmann)"],
        "weight": 15,
        "always_active": False,
        "activation": "service/API project detected",
    },
    "H6": {
        "name": "Enterprise Patterns",
        "sources": ["PoEAA (Fowler)"],
        "weight": 10,
        "always_active": False,
        "activation": "enterprise patterns detected (repository/, services/ dirs)",
    },
    "H7": {
        "name": "Engineering Practice",
        "sources": ["The Pragmatic Programmer (Hunt/Thomas)"],
        "weight": 20,
        "always_active": True,
    },
}


# ---------------------------------------------------------------------------
# Project context detection
# ---------------------------------------------------------------------------

def _detect_context(root: Path) -> dict[str, bool]:
    """Detect which heuristic categories should be activated."""
    context: dict[str, bool] = {}

    # Count Python modules
    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f) and "node_modules" not in str(f)]
    pkg_dirs = set()
    for f in py_files:
        if f.parent != root:
            pkg_dirs.add(f.parent)

    context["has_modules"] = len(pkg_dirs) > 5

    # Architecture directories
    arch_dirs = {"domain", "ports", "adapters", "infrastructure", "entities",
                 "use_cases", "interfaces", "core"}
    found_arch = [d.name for d in root.rglob("*") if d.is_dir() and d.name in arch_dirs
                  and ".venv" not in str(d)]
    context["has_architecture"] = len(found_arch) >= 2

    # DDD patterns
    ddd_dirs = {"domain", "entities", "aggregates", "value_objects", "bounded_contexts"}
    found_ddd = [d.name for d in root.rglob("*") if d.is_dir() and d.name in ddd_dirs
                 and ".venv" not in str(d)]
    context["has_ddd"] = len(found_ddd) >= 2

    # Service/API detection
    service_indicators = {"fastapi", "flask", "django", "uvicorn", "gunicorn",
                          "aiohttp", "starlette", "sanic"}
    deps = _read_deps(root)
    context["is_service"] = bool(service_indicators & set(deps))

    # Enterprise patterns
    enterprise_dirs = {"repository", "repositories", "services", "handlers",
                       "controllers", "gateways"}
    found_enterprise = [d.name for d in root.rglob("*") if d.is_dir()
                        and d.name in enterprise_dirs and ".venv" not in str(d)]
    context["has_enterprise"] = len(found_enterprise) >= 2

    return context


def _read_deps(root: Path) -> list[str]:
    """Read dependency names from pyproject.toml."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return []
    try:
        import tomllib
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        deps = []
        for d in data.get("project", {}).get("dependencies", []):
            name = re.split(r"[\[<>=~!;]", d)[0].strip().lower()
            if name:
                deps.append(name)
        return deps
    except Exception:
        return []


def _activate_categories(context: dict[str, bool]) -> dict[str, dict]:
    """Return only the active heuristic categories with normalized weights."""
    active = {}
    for cat_id, cat in HEURISTIC_CATEGORIES.items():
        if cat["always_active"]:
            active[cat_id] = cat
        elif cat_id == "H2" and (context.get("has_modules") or context.get("has_architecture")):
            active[cat_id] = cat
        elif cat_id == "H4" and context.get("has_ddd"):
            active[cat_id] = cat
        elif cat_id == "H5" and context.get("is_service"):
            active[cat_id] = cat
        elif cat_id == "H6" and context.get("has_enterprise"):
            active[cat_id] = cat

    # Normalize weights
    total_weight = sum(c["weight"] for c in active.values())
    if total_weight > 0:
        for cat in active.values():
            cat["normalized_weight"] = round(cat["weight"] / total_weight * 100, 1)

    return active


# ---------------------------------------------------------------------------
# Heuristic checks — each returns (score 0-100, findings list)
# ---------------------------------------------------------------------------

def _scan_python_functions(root: Path) -> list[dict]:
    """Parse Python files and extract function metrics."""
    functions: list[dict] = []
    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f)
                and "node_modules" not in str(f) and "__pycache__" not in str(f)]

    for py_file in py_files[:200]:  # Cap to avoid slowdowns
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno + 10)
                length = end_line - node.lineno + 1
                param_count = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
                # Approximate nesting depth
                max_depth = _max_nesting(node)
                functions.append({
                    "name": node.name,
                    "file": str(py_file.relative_to(root)),
                    "length": length,
                    "params": param_count,
                    "nesting": max_depth,
                })

    return functions


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    """Calculate maximum nesting depth in an AST node."""
    max_d = depth
    nesting_types = (ast.If, ast.For, ast.While, ast.With, ast.Try,
                     ast.AsyncFor, ast.AsyncWith)
    for child in ast.iter_child_nodes(node):
        if isinstance(child, nesting_types):
            max_d = max(max_d, _max_nesting(child, depth + 1))
        else:
            max_d = max(max_d, _max_nesting(child, depth))
    return max_d


def check_h1_construction(root: Path, functions: list[dict]) -> tuple[int, list[str]]:
    """H1: Construction Quality — Clean Code + Code Complete."""
    score = 100
    findings: list[str] = []

    if not functions:
        return 70, ["No Python functions found to analyze"]

    # Function length
    long_fns = [f for f in functions if f["length"] > 50]
    long_pct = len(long_fns) / len(functions) * 100 if functions else 0
    if long_pct > 20:
        score -= 20
        findings.append(f"{len(long_fns)} functions ({long_pct:.0f}%) exceed 50 lines [Clean Code: keep functions small]")
    elif long_pct > 10:
        score -= 10
        findings.append(f"{len(long_fns)} functions ({long_pct:.0f}%) exceed 50 lines")
    elif long_pct > 5:
        score -= 5

    # Parameter count
    many_params = [f for f in functions if f["params"] > 5]
    if many_params:
        pct = len(many_params) / len(functions) * 100
        deduction = min(15, int(pct))
        score -= deduction
        findings.append(f"{len(many_params)} functions have >5 parameters [Clean Code: few and meaningful params]")

    # Nesting depth
    deep_fns = [f for f in functions if f["nesting"] > 4]
    if deep_fns:
        deduction = min(15, len(deep_fns) * 3)
        score -= deduction
        findings.append(f"{len(deep_fns)} functions have nesting depth >4 [Code Complete: straightforward control flow]")

    # Average function length
    avg_len = sum(f["length"] for f in functions) / len(functions)
    if avg_len > 50:
        score -= 10
        findings.append(f"Average function length {avg_len:.0f} lines [target: <20]")
    elif avg_len > 35:
        score -= 5

    return max(0, score), findings


def check_h2_architecture(root: Path) -> tuple[int, list[str]]:
    """H2: Architecture Boundaries — Clean Architecture + Philosophy of Software Design."""
    score = 100
    findings: list[str] = []

    # Check dependency direction: domain modules should not import from infrastructure
    domain_dirs = set()
    infra_dirs = set()
    for d in root.rglob("*"):
        if not d.is_dir() or ".venv" in str(d):
            continue
        if d.name in ("domain", "entities", "core", "models"):
            domain_dirs.add(d)
        if d.name in ("infrastructure", "adapters", "drivers", "external"):
            infra_dirs.add(d)

    # Scan domain files for infrastructure imports
    violations = 0
    infra_names = {d.name for d in infra_dirs}
    for domain_dir in domain_dirs:
        for py_file in domain_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                for infra_name in infra_names:
                    if f"from {infra_name}" in content or f"import {infra_name}" in content:
                        violations += 1
            except Exception:
                pass

    if violations > 10:
        score -= 25
        findings.append(f"{violations} dependency rule violations: domain imports infrastructure [Clean Architecture: deps point toward policy]")
    elif violations > 5:
        score -= 15
        findings.append(f"{violations} dependency rule violations found")
    elif violations > 0:
        score -= 5
        findings.append(f"{violations} minor dependency direction violation(s)")

    # Check for feature-oriented vs layer-oriented structure
    top_dirs = [d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    layer_names = {"controllers", "services", "repositories", "models", "views"}
    if len(layer_names & set(top_dirs)) >= 3:
        score -= 10
        findings.append("Layer-oriented structure detected [Clean Architecture: prefer feature-oriented]")

    return max(0, score), findings


def check_h3_refactoring(root: Path) -> tuple[int, list[str]]:
    """H3: Refactoring Discipline — Refactoring + Legacy Code."""
    score = 100
    findings: list[str] = []

    # Check for test presence (safety net before refactoring)
    has_tests = (root / "tests").is_dir() or (root / "test").is_dir()
    if not has_tests:
        score -= 30
        findings.append("No tests directory [Refactoring: get a safety net first]")

    # Check for pre-commit (verification pipeline)
    if not (root / ".pre-commit-config.yaml").exists():
        score -= 10
        findings.append("No pre-commit config [Pragmatic Programmer: automate verification]")

    # Check for type hints usage (safety signal)
    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f)]
    typed_count = 0
    sample = py_files[:50]
    for pf in sample:
        try:
            content = pf.read_text(encoding="utf-8", errors="replace")
            if re.search(r"def \w+\([^)]*:\s*\w+", content) or "-> " in content:
                typed_count += 1
        except Exception:
            pass

    if sample:
        type_ratio = typed_count / len(sample)
        if type_ratio < 0.3:
            score -= 15
            findings.append(f"Low type hint coverage ({type_ratio:.0%}) [Legacy Code: make assumptions explicit]")
        elif type_ratio < 0.6:
            score -= 5

    return max(0, score), findings


def check_h4_domain_modeling(root: Path) -> tuple[int, list[str]]:
    """H4: Domain Modeling — DDD books."""
    score = 100
    findings: list[str] = []

    # Check aggregate size (should be small)
    aggregate_dirs = list(root.rglob("aggregates"))
    aggregate_dirs = [d for d in aggregate_dirs if d.is_dir() and ".venv" not in str(d)]
    for agg_dir in aggregate_dirs:
        files = list(agg_dir.rglob("*.py"))
        if len(files) > 10:
            score -= 10
            findings.append(f"Large aggregate directory ({len(files)} files) [DDD: keep aggregates small]")

    # Check that domain logic is in domain layer, not services
    services_dir = root / "services"
    if services_dir.is_dir():
        for svc_file in services_dir.rglob("*.py"):
            try:
                content = svc_file.read_text(encoding="utf-8", errors="replace")
                # Look for business logic indicators in service files
                biz_patterns = len(re.findall(r"if.*(?:validate|check|verify|calculate|compute)", content))
                if biz_patterns > 5:
                    score -= 10
                    findings.append(f"Business logic in service layer: {svc_file.name} [DDD: domain rules in domain layer]")
                    break
            except Exception:
                pass

    return max(0, score), findings


def check_h5_resilience(root: Path) -> tuple[int, list[str]]:
    """H5: Production Resilience — Release It! + DDIA."""
    score = 100
    findings: list[str] = []

    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f)]

    http_calls_total = 0
    http_calls_with_timeout = 0
    has_retry = False
    has_circuit_breaker = False

    for pf in py_files[:100]:
        try:
            content = pf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Timeout coverage on HTTP calls
        http_patterns = re.findall(r"(requests\.\w+|httpx\.\w+|aiohttp\.\w+)\(", content)
        http_calls_total += len(http_patterns)
        timeout_patterns = re.findall(r"timeout\s*=", content)
        http_calls_with_timeout += len(timeout_patterns)

        # Retry patterns
        if re.search(r"retry|tenacity|backoff|Retry", content):
            has_retry = True

        # Circuit breaker
        if re.search(r"circuit.?breaker|CircuitBreaker|pybreaker", content):
            has_circuit_breaker = True

    if http_calls_total > 0:
        timeout_ratio = http_calls_with_timeout / http_calls_total
        if timeout_ratio < 0.5:
            score -= 20
            findings.append(f"Low timeout coverage ({timeout_ratio:.0%}) on HTTP calls [Release It!: timeout all external calls]")
        elif timeout_ratio < 0.8:
            score -= 10
            findings.append(f"Partial timeout coverage ({timeout_ratio:.0%}) on HTTP calls")

    if not has_retry and http_calls_total > 3:
        score -= 15
        findings.append("No retry/backoff patterns detected [Release It!: bounded retries with backoff]")

    if not has_circuit_breaker and http_calls_total > 5:
        score -= 10
        findings.append("No circuit breaker pattern [Release It!: isolate failure]")

    return max(0, score), findings


def check_h6_enterprise(root: Path) -> tuple[int, list[str]]:
    """H6: Enterprise Patterns — PoEAA."""
    score = 100
    findings: list[str] = []

    # Check for explicit transaction boundaries
    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f)]

    has_transaction = False
    has_thin_service = True

    for pf in py_files[:80]:
        try:
            content = pf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if re.search(r"transaction|commit|rollback|atomic|session\.begin", content):
            has_transaction = True

        # Check for fat services (anti-pattern)
        if "service" in pf.name.lower():
            lines = content.split("\n")
            if len(lines) > 300:
                has_thin_service = False

    if not has_transaction:
        score -= 10
        findings.append("No explicit transaction boundaries [PoEAA: make transaction boundaries explicit]")

    if not has_thin_service:
        score -= 10
        findings.append("Fat service detected (>300 lines) [PoEAA: service layer coordinates, doesn't compute]")

    return max(0, score), findings


def check_h7_practice(root: Path) -> tuple[int, list[str]]:
    """H7: Engineering Practice — The Pragmatic Programmer."""
    score = 100
    findings: list[str] = []

    # CI/automation presence
    has_ci = (root / ".github" / "workflows").is_dir() or (root / ".gitlab-ci.yml").exists()
    has_precommit = (root / ".pre-commit-config.yaml").exists()
    has_makefile = (root / "Makefile").exists() or (root / "justfile").exists()
    automation_count = sum([has_ci, has_precommit, has_makefile])

    if automation_count == 0:
        score -= 20
        findings.append("No automation (CI/pre-commit/Makefile) [Pragmatic: automate repetitive work]")
    elif automation_count == 1:
        score -= 10
        findings.append(f"Partial automation ({automation_count}/3) [Pragmatic: shorten feedback loops]")

    # DRY check — look for near-duplicate files
    py_files = list(root.rglob("*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f)
                and "test" not in str(f).lower()]

    # Simple duplicate detection: files with very similar sizes in same package
    # (Real dedup would use AST/hash comparison)
    size_clusters: dict[int, list[str]] = {}
    for pf in py_files[:100]:
        try:
            size = pf.stat().st_size
            bucket = size // 100  # 100-byte buckets
            size_clusters.setdefault(bucket, []).append(str(pf.relative_to(root)))
        except Exception:
            pass

    potential_dupes = sum(1 for cluster in size_clusters.values() if len(cluster) > 2)
    if potential_dupes > 5:
        score -= 10
        findings.append(f"{potential_dupes} potential duplicate clusters [Pragmatic: DRY at knowledge level]")

    # Broken windows — check for TODO/FIXME/HACK density
    issue_count = 0
    for pf in py_files[:80]:
        try:
            content = pf.read_text(encoding="utf-8", errors="replace")
            issue_count += len(re.findall(r"#\s*(TODO|FIXME|HACK|XXX)\b", content))
        except Exception:
            pass

    if issue_count > 20:
        score -= 10
        findings.append(f"{issue_count} TODO/FIXME/HACK markers [Pragmatic: fix broken windows]")
    elif issue_count > 10:
        score -= 5

    return max(0, score), findings


# ---------------------------------------------------------------------------
# Main evaluation pipeline
# ---------------------------------------------------------------------------

CATEGORY_CHECKERS = {
    "H1": check_h1_construction,
    "H2": check_h2_architecture,
    "H3": check_h3_refactoring,
    "H4": check_h4_domain_modeling,
    "H5": check_h5_resilience,
    "H6": check_h6_enterprise,
    "H7": check_h7_practice,
}


def evaluate_heuristics(root_dir: str = ".") -> dict:
    """Evaluate engineering heuristics for a project.

    Returns standard code-enhancer domain result dict.
    """
    root = Path(root_dir).resolve()

    # Detect context
    context = _detect_context(root)
    active = _activate_categories(context)

    if not active:
        return {
            "domain": "Engineering Heuristics",
            "score": -1,
            "grade": "N/A",
            "findings": ["No heuristic categories activated"],
            "justifications": [],
            "details": {"context": context, "active_categories": []},
        }

    # Pre-scan functions once (shared by H1)
    functions = _scan_python_functions(root)

    # Run each active category
    category_results: list[dict] = []
    all_findings: list[str] = []
    weighted_total = 0.0
    weight_sum = 0.0

    for cat_id, cat in active.items():
        checker = CATEGORY_CHECKERS.get(cat_id)
        if not checker:
            continue

        if cat_id == "H1":
            cat_score, cat_findings = checker(root, functions)
        else:
            cat_score, cat_findings = checker(root)

        norm_weight = cat.get("normalized_weight", cat["weight"])
        weighted_total += cat_score * norm_weight / 100
        weight_sum += norm_weight

        category_results.append({
            "id": cat_id,
            "name": cat["name"],
            "sources": cat["sources"],
            "score": cat_score,
            "grade": _score_to_grade(cat_score),
            "weight": norm_weight,
            "findings": cat_findings,
        })

        if cat_findings:
            all_findings.append(f"**{cat['name']}** ({cat_score}/100):")
            for f in cat_findings:
                all_findings.append(f"  - {f}")

    # Compute weighted aggregate
    aggregate = round(weighted_total) if weight_sum > 0 else 0

    justifications = []
    for cr in category_results:
        justifications.append({
            "criterion": cr["name"],
            "points": cr["score"],
            "evidence": f"Sources: {', '.join(cr['sources'])}",
            "reasoning": f"Score {cr['score']}/100, weight {cr['weight']:.0f}%"
                         + (f" — {cr['findings'][0]}" if cr["findings"] else ""),
        })

    return {
        "domain": "Engineering Heuristics",
        "score": aggregate,
        "grade": _score_to_grade(aggregate),
        "findings": all_findings,
        "justifications": justifications,
        "details": {
            "context": context,
            "active_categories": [c["name"] for c in category_results],
            "category_count": len(category_results),
            "functions_analyzed": len(functions),
        },
        "category_results": category_results,
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


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    results = evaluate_heuristics(target)
    print(json.dumps(results, indent=2))

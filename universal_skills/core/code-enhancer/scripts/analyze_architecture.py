#!/usr/bin/env python3
"""FR-011: Architecture pattern evaluation for code-enhancer skill.

Evaluates codebase against SOLID, hexagonal, clean architecture patterns,
dependency injection, event-driven design, and large-codebase scaling.

CONCEPT:CE-011 — Architecture & Design Patterns
"""

import ast
import json
import re
import sys
from pathlib import Path


def _check_solid_principles(root: Path, py_files: list[Path]) -> list[dict]:
    """Evaluate SOLID principle adherence."""
    findings: list[dict] = []
    large_classes: list[dict] = []
    god_modules: list[dict] = []

    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue

        lines = len(source.splitlines())
        # Single Responsibility: files >500 lines
        if lines > 500:
            god_modules.append({"file": str(f), "lines": lines})

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if len(methods) > 15:
                    large_classes.append(
                        {
                            "class": node.name,
                            "file": str(f),
                            "method_count": len(methods),
                        }
                    )

    if god_modules:
        findings.append(
            {
                "principle": "SRP",
                "status": "violation",
                "detail": f"{len(god_modules)} modules exceed 500 lines (god modules)",
                "items": god_modules[:5],
            }
        )
    if large_classes:
        findings.append(
            {
                "principle": "SRP",
                "status": "violation",
                "detail": f"{len(large_classes)} classes have >15 methods",
                "items": large_classes[:5],
            }
        )

    return findings


def _check_layered_architecture(root: Path) -> dict:
    """Check for layered/hexagonal architecture patterns."""
    indicators = {
        "has_domain_layer": False,
        "has_adapter_layer": False,
        "has_port_interfaces": False,
        "has_service_layer": False,
        "has_model_layer": False,
    }

    # Check for common layer directory patterns
    layer_patterns = {
        "has_domain_layer": ["domain", "core", "entities"],
        "has_adapter_layer": ["adapters", "infrastructure", "external"],
        "has_port_interfaces": ["ports", "interfaces", "contracts"],
        "has_service_layer": ["services", "application", "use_cases", "usecases"],
        "has_model_layer": ["models", "schemas"],
    }

    for indicator, patterns in layer_patterns.items():
        for p in patterns:
            if any(
                d.name == p
                for d in root.rglob("*")
                if d.is_dir()
                and ".venv" not in d.parts
                and "__pycache__" not in d.parts
            ):
                indicators[indicator] = True
                break

    return indicators


def _check_dependency_injection(py_files: list[Path]) -> dict:
    """Check for dependency injection patterns."""
    di_count = 0
    total_classes = 0

    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                total_classes += 1
                # Check if __init__ accepts dependencies as parameters
                for method in node.body:
                    if (
                        isinstance(method, ast.FunctionDef)
                        and method.name == "__init__"
                    ):
                        # More than just 'self' parameter with type annotations
                        annotated_params = [
                            a
                            for a in method.args.args[1:]  # skip self
                            if a.annotation is not None
                        ]
                        if len(annotated_params) >= 2:
                            di_count += 1

    return {
        "total_classes": total_classes,
        "di_classes": di_count,
        "di_ratio": round(di_count / max(total_classes, 1), 2),
    }


def _check_event_driven(py_files: list[Path]) -> dict:
    """Check for event-driven patterns."""
    event_indicators = {
        "event_classes": 0,
        "callback_patterns": 0,
        "observer_patterns": 0,
        "signal_patterns": 0,
    }

    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        source_lower = source.lower()
        event_indicators["event_classes"] += len(
            re.findall(r"class\s+\w*Event\w*", source)
        )
        event_indicators["callback_patterns"] += source_lower.count("callback")
        event_indicators["observer_patterns"] += source_lower.count(
            "observer"
        ) + source_lower.count("listener")
        event_indicators["signal_patterns"] += source_lower.count(
            "signal"
        ) + source_lower.count("emit")

    return event_indicators


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


def analyze_architecture(root_dir: str = ".") -> dict:
    """Analyze architecture patterns and produce scored results."""
    root = Path(root_dir).resolve()
    py_files = [
        f
        for f in root.rglob("*.py")
        if ".venv" not in f.parts
        and "__pycache__" not in f.parts
        and "node_modules" not in f.parts
        and ".git" not in f.parts
    ]

    if not py_files:
        return {
            "domain": "Architecture & Design Patterns",
            "score": 0,
            "grade": "F",
            "findings": ["No Python files found"],
            "justifications": [],
            "analysis": {},
        }

    # Run analyses
    solid = _check_solid_principles(root, py_files)
    layers = _check_layered_architecture(root)
    di = _check_dependency_injection(py_files)
    events = _check_event_driven(py_files)

    # Scoring
    score = 100
    findings: list[str] = []

    # SOLID violations (-5 per type)
    srp_violations = [f for f in solid if f["principle"] == "SRP"]
    if srp_violations:
        penalty = min(20, len(srp_violations) * 5)
        score -= penalty
        for v in srp_violations:
            findings.append(f"SRP: {v['detail']}")

    # Layer architecture (+10 for good structure)
    layer_count = sum(1 for v in layers.values() if v)
    if layer_count >= 3:
        pass  # Good architecture, no deduction
    elif layer_count >= 2:
        score -= 5
    elif layer_count >= 1:
        score -= 10
    else:
        score -= 15
        findings.append(
            "No discernible layer architecture (no domain/service/adapter separation)"
        )

    # DI ratio
    if di["total_classes"] > 5 and di["di_ratio"] < 0.1:
        score -= 10
        findings.append(f"Low dependency injection ratio: {di['di_ratio']:.0%}")
    elif di["total_classes"] > 5 and di["di_ratio"] < 0.3:
        score -= 5

    # Module organization
    if len(py_files) > 50:
        # Large codebase: check for package organization
        top_level_py = [f for f in py_files if len(f.relative_to(root).parts) <= 2]
        if len(top_level_py) > 20:
            score -= 10
            findings.append(
                f"{len(top_level_py)} Python files at top level — consider package organization"
            )

    score = max(0, score)

    analysis = {
        "solid_findings": solid,
        "layer_architecture": layers,
        "dependency_injection": di,
        "event_driven": events,
        "file_count": len(py_files),
    }

    justifications = [
        {
            "criterion": "architecture_quality",
            "points": score,
            "evidence": json.dumps(
                {
                    "layers": layer_count,
                    "di_ratio": di["di_ratio"],
                    "solid_violations": len(solid),
                }
            ),
            "reasoning": (
                f"Analyzed {len(py_files)} files. "
                f"{layer_count}/5 architecture layers present, "
                f"DI ratio: {di['di_ratio']:.0%}, "
                f"{len(solid)} SOLID violations."
            ),
        }
    ]

    return {
        "domain": "Architecture & Design Patterns",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "analysis": analysis,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze_architecture(target), indent=2))

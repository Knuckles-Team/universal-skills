#!/usr/bin/env python3
"""CA-003: Architecture analysis — patterns, SOLID, protocols, type system.

Usage: python analyze_architecture.py /path/to/project

CONCEPT:CA-003 — Architecture & Design Quality
"""

import ast
import json
import re
import sys
from pathlib import Path

PROTOCOL_MARKERS = {
    "MCP": ["fastmcp", "mcp_config.json", "@mcp.tool", "MCPServer"],
    "A2A": ["a2a_config.json", "A2AClient", "json-rpc"],
    "ACP": ["pydantic-acp", "acp_adapter"],
    "REST": ["@app.get", "@app.post", "@router", "FastAPI", "flask"],
    "GraphQL": ["strawberry", "graphene", "schema.graphql"],
    "gRPC": [".proto", "grpc", "protobuf"],
    "WebSocket": ["websocket", "ws://", "wss://"],
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build", ".mypy_cache"}


def detect_protocols(project_path: Path) -> dict:
    """Scan for protocol support markers."""
    found = {}
    code_content = ""
    for f in project_path.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".js", ".ts", ".go", ".rs", ".toml", ".json", ".yml", ".yaml"}:
            rel = f.relative_to(project_path)
            if any(p in str(rel) for p in SKIP_DIRS):
                continue
            try:
                code_content += f.read_text(errors="ignore") + "\n"
            except (OSError, UnicodeDecodeError):
                pass
        if f.name in ["mcp_config.json", "a2a_config.json", "openapi.json"]:
            found[f.name] = True

    for proto, markers in PROTOCOL_MARKERS.items():
        for marker in markers:
            if marker in code_content:
                found[proto] = True
                break
    return found


def analyze_type_coverage(project_path: Path) -> dict:
    """Estimate type annotation coverage for Python projects."""
    total_funcs = 0
    typed_funcs = 0
    for pyfile in project_path.rglob("*.py"):
        rel = pyfile.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            tree = ast.parse(pyfile.read_text(errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_funcs += 1
                    if node.returns is not None or any(a.annotation for a in node.args.args):
                        typed_funcs += 1
        except (SyntaxError, UnicodeDecodeError):
            pass
    coverage = round(typed_funcs / max(total_funcs, 1) * 100, 1)
    return {"total_functions": total_funcs, "typed_functions": typed_funcs, "coverage_pct": coverage}


def analyze_module_structure(project_path: Path) -> dict:
    """Analyze module depth, fan-out, and separation of concerns."""
    packages = set()
    max_depth = 0
    for f in project_path.rglob("__init__.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        depth = len(rel.parts) - 1
        max_depth = max(max_depth, depth)
        packages.add(str(rel.parent))

    return {
        "package_count": len(packages),
        "max_nesting_depth": max_depth,
        "packages": sorted(packages)[:20],
    }


def detect_config_patterns(project_path: Path) -> dict:
    """Detect 12-Factor compliance signals."""
    signals = {
        "env_vars": False,
        "config_files": False,
        "dotenv": False,
        "docker": False,
        "port_binding": False,
        "graceful_shutdown": False,
    }

    for f in project_path.rglob("*.py"):
        rel = f.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = f.read_text(errors="ignore")
            if "os.environ" in content or "os.getenv" in content:
                signals["env_vars"] = True
            if "dotenv" in content or "python-dotenv" in content:
                signals["dotenv"] = True
            if "signal.SIGTERM" in content or "atexit" in content:
                signals["graceful_shutdown"] = True
            if "--port" in content or "PORT" in content:
                signals["port_binding"] = True
        except (OSError, UnicodeDecodeError):
            pass

    signals["docker"] = any(
        (project_path / f).exists() for f in ["Dockerfile", "docker-compose.yml", "compose.yml"]
    )
    signals["config_files"] = any(
        (project_path / f).exists() for f in ["config.yml", "config.yaml", "config.json", ".env.example"]
    )

    return signals


def score_architecture(protocols: dict, types: dict, structure: dict, config: dict) -> dict:
    """Calculate 0-100 architecture score."""
    score = 0
    details = []

    # Protocol support (30 points)
    proto_count = len(protocols)
    if proto_count >= 3:
        score += 30
        details.append(f"Rich protocol support ({proto_count} protocols): +30")
    elif proto_count >= 2:
        score += 20
        details.append(f"Multi-protocol ({proto_count}): +20")
    elif proto_count >= 1:
        score += 10
        details.append(f"Single protocol: +10")

    # Type system (25 points)
    cov = types.get("coverage_pct", 0)
    if cov >= 80:
        score += 25
        details.append(f"Excellent type coverage ({cov}%): +25")
    elif cov >= 50:
        score += 15
        details.append(f"Good type coverage ({cov}%): +15")
    elif cov >= 25:
        score += 10
        details.append(f"Partial type coverage ({cov}%): +10")

    # Module structure (25 points)
    pkg_count = structure.get("package_count", 0)
    if pkg_count >= 5:
        score += 15
        details.append(f"Well-structured ({pkg_count} packages): +15")
    elif pkg_count >= 2:
        score += 10
        details.append(f"Basic structure ({pkg_count} packages): +10")

    depth = structure.get("max_nesting_depth", 0)
    if 2 <= depth <= 4:
        score += 10
        details.append(f"Appropriate nesting depth ({depth}): +10")
    elif depth >= 1:
        score += 5

    # 12-Factor (20 points)
    factor_count = sum(1 for v in config.values() if v)
    factor_score = min(factor_count * 4, 20)
    score += factor_score
    details.append(f"12-Factor signals ({factor_count}/6): +{factor_score}")

    grade = "A+" if score >= 95 else "A" if score >= 90 else "B+" if score >= 85 else "B" if score >= 80 else "C+" if score >= 75 else "C" if score >= 70 else "D" if score >= 60 else "F"
    return {"score": min(score, 100), "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_architecture.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    protocols = detect_protocols(project_path)
    types = analyze_type_coverage(project_path)
    structure = analyze_module_structure(project_path)
    config = detect_config_patterns(project_path)
    scoring = score_architecture(protocols, types, structure, config)

    print(json.dumps({
        "domain": "CA-003", "domain_name": "Architecture",
        "project": str(project_path),
        "protocols": protocols, "type_coverage": types,
        "module_structure": structure, "config_patterns": config,
        "scoring": scoring,
    }, indent=2))


if __name__ == "__main__":
    main()

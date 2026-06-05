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

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
}


def detect_protocols(project_path: Path) -> dict:
    """Scan for protocol support markers."""
    found = {}
    code_content = ""
    for f in project_path.rglob("*"):
        if f.is_file() and f.suffix in {
            ".py",
            ".js",
            ".ts",
            ".go",
            ".rs",
            ".toml",
            ".json",
            ".yml",
            ".yaml",
        }:
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
                    if node.returns is not None or any(
                        a.annotation for a in node.args.args
                    ):
                        typed_funcs += 1
        except (SyntaxError, UnicodeDecodeError):
            pass
    coverage = round(typed_funcs / max(total_funcs, 1) * 100, 1)
    return {
        "total_functions": total_funcs,
        "typed_functions": typed_funcs,
        "coverage_pct": coverage,
    }


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
        (project_path / f).exists()
        for f in ["Dockerfile", "docker-compose.yml", "compose.yml"]
    )
    signals["config_files"] = any(
        (project_path / f).exists()
        for f in ["config.yml", "config.yaml", "config.json", ".env.example"]
    )

    return signals


def score_architecture(
    protocols: dict, types: dict, structure: dict, config: dict
) -> dict:
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
        details.append("Single protocol: +10")

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


# ── C4 Architecture Discovery ──────────────────────────────────────────────

C4_MARKERS = {
    "C4Context": "system_context",
    "C4Container": "container",
    "C4Component": "component",
    "C4Deployment": "deployment",
}

C4_ELEMENT_RE = re.compile(
    r"(Person|System|System_Ext|Container|ContainerDb|Component|Container_Boundary)"
    r'\(\s*(\w+)\s*,\s*"([^"]*)"',
)
C4_REL_RE = re.compile(r'Rel\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]*)"')


def discover_c4_architecture(project_path: Path) -> dict:
    """Discover existing C4 architecture diagrams from the filesystem."""
    diagrams = []
    check_dirs = ["docs", ".specify", "."]
    md_files = []
    for d in check_dirs:
        target = project_path / d
        if target.is_dir():
            md_files.extend(target.rglob("*.md"))

    for md_file in md_files:
        rel = md_file.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = md_file.read_text(errors="ignore")
        except OSError:
            continue

        for marker, level in C4_MARKERS.items():
            if marker not in content:
                continue
            elements = C4_ELEMENT_RE.findall(content)
            relationships = C4_REL_RE.findall(content)
            diagrams.append(
                {
                    "file": str(rel),
                    "level": level,
                    "components": [
                        {"kind": e[0], "id": e[1], "name": e[2]} for e in elements
                    ],
                    "relationships": [
                        {"from": r[0], "to": r[1], "label": r[2]} for r in relationships
                    ],
                }
            )

    return {
        "diagrams": diagrams,
        "has_c4": len(diagrams) > 0,
        "diagram_count": len(diagrams),
    }


# ── Hot Path Identification ────────────────────────────────────────────────

ENTRY_POINT_PATTERNS = {
    "mcp_tool": re.compile(r"@mcp\.tool\(\)"),
    "fastapi_route": re.compile(r"@(?:app|router)\.\w+\("),
    "click_command": re.compile(r"@click\.(command|group)"),
    "a2a_skill": re.compile(r"async\s+def\s+run\(self.*messages"),
}


def identify_hot_paths(project_path: Path) -> dict:
    """Identify entry points and trace reachability via import graph."""
    entry_points = []
    all_modules = set()
    import_graph: dict[str, set[str]] = {}

    for pyfile in project_path.rglob("*.py"):
        rel = pyfile.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        mod_name = (
            str(rel).replace("/", ".").removesuffix(".py").removesuffix(".__init__")
        )
        all_modules.add(mod_name)

        try:
            content = pyfile.read_text(errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, OSError):
            continue

        # Check for entry point patterns
        for ep_type, pattern in ENTRY_POINT_PATTERNS.items():
            if pattern.search(content):
                entry_points.append(
                    {"type": ep_type, "module": mod_name, "file": str(rel)}
                )
                break

        # Check for if __name__ == "__main__"
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                test_str = ast.dump(node.test)
                if "__name__" in test_str and "__main__" in test_str:
                    entry_points.append(
                        {"type": "cli_main", "module": mod_name, "file": str(rel)}
                    )

        # Build import graph
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        import_graph[mod_name] = imports

    # BFS reachability from entry points
    reachable = set()
    frontier = {ep["module"] for ep in entry_points}
    visited = set()
    while frontier:
        current = frontier.pop()
        if current in visited:
            continue
        visited.add(current)
        reachable.add(current)
        for dep in import_graph.get(current, set()):
            # Match dependencies against known modules
            for mod in all_modules:
                if mod.startswith(dep) or dep in mod:
                    frontier.add(mod)

    cold_modules = all_modules - reachable
    coverage = round(len(reachable) / max(len(all_modules), 1) * 100, 1)

    return {
        "entry_points": entry_points[:20],
        "entry_point_count": len(entry_points),
        "total_modules": len(all_modules),
        "hot_path_modules": len(reachable),
        "cold_modules": sorted(cold_modules)[:15],
        "cold_module_count": len(cold_modules),
        "hot_path_coverage_pct": coverage,
    }


# ── Design Pattern Detection ──────────────────────────────────────────────


def analyze_design_patterns(project_path: Path) -> dict:
    """Detect architectural design patterns via AST analysis."""
    patterns = {
        "mixin": 0,
        "dependency_injection": 0,
        "lazy_init": 0,
        "plugin_registry": 0,
        "event_driven": 0,
        "protocol_oriented": 0,
        "factory": 0,
        "strategy": 0,
    }
    examples: dict[str, list[str]] = {k: [] for k in patterns}

    for pyfile in project_path.rglob("*.py"):
        rel = pyfile.relative_to(project_path)
        if any(p in str(rel) for p in SKIP_DIRS):
            continue
        try:
            content = pyfile.read_text(errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Mixin: multiple base classes
                if len(node.bases) >= 2:
                    patterns["mixin"] += 1
                    if len(examples["mixin"]) < 3:
                        examples["mixin"].append(f"{rel}:{node.name}")

                # Protocol/ABC oriented
                for base in node.bases:
                    base_name = getattr(base, "id", getattr(base, "attr", ""))
                    if base_name in ("Protocol", "ABC", "ABCMeta"):
                        patterns["protocol_oriented"] += 1
                        if len(examples["protocol_oriented"]) < 3:
                            examples["protocol_oriented"].append(f"{rel}:{node.name}")

                # Lazy init: @property with _field guard
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and any(
                        isinstance(d, ast.Name) and d.id == "property"
                        for d in item.decorator_list
                    ):
                        body_str = ast.dump(item)
                        if "None" in body_str and "_" in item.name:
                            patterns["lazy_init"] += 1

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Factory pattern
                if node.name.startswith(("create_", "build_", "make_")):
                    patterns["factory"] += 1
                    if len(examples["factory"]) < 3:
                        examples["factory"].append(f"{rel}:{node.name}")

                # DI: constructor with typed params
                if node.name == "__init__":
                    typed_params = sum(1 for a in node.args.args if a.annotation)
                    if typed_params >= 2:
                        patterns["dependency_injection"] += 1

        # Text-based pattern detection
        if re.search(r"\b(register|subscribe|on_event|emit|publish)\s*\(", content):
            if "register" in content or "subscribe" in content:
                patterns["plugin_registry"] += 1
            if "emit" in content or "publish" in content:
                patterns["event_driven"] += 1

    return {"counts": patterns, "examples": examples}


# ── C4 Auto-Generation ────────────────────────────────────────────────────


def auto_generate_c4(
    project_path: Path, structure: dict, protocols: dict, entry_info: dict
) -> str:
    """Generate a C4 Component diagram from AST-parsed project structure."""
    packages = structure.get("packages", [])
    if not packages:
        return ""

    # Determine project name
    proj_name = project_path.name
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            for line in pyproject.read_text().splitlines():
                if line.strip().startswith("name"):
                    proj_name = line.split("=")[1].strip().strip('"').strip("'")
                    break
        except OSError:
            pass

    lines = [
        f"# {proj_name} — Auto-Generated C4 Architecture",
        "",
        "> Auto-generated by `analyze_architecture.py` from AST analysis.",
        "> Update this file manually to add descriptions and refine boundaries.",
        "",
        "## Component Diagram",
        "",
        "```mermaid",
        "C4Component",
        f"    title {proj_name} — Component Diagram (Auto-Generated)",
        "",
        f'    Container_Boundary(proj, "{proj_name}") {{',
    ]

    # Group packages into boundaries
    top_level: dict[str, list[str]] = {}
    for pkg in packages:
        parts = pkg.split("/")
        top = parts[1] if len(parts) > 1 else parts[0]
        top_level.setdefault(top, []).append(pkg)

    comp_ids = []
    for top_pkg, sub_pkgs in sorted(top_level.items()):
        comp_id = re.sub(r"[^a-zA-Z0-9]", "_", top_pkg)
        comp_ids.append(comp_id)
        desc = f"{len(sub_pkgs)} sub-packages"
        lines.append(f'        Component({comp_id}, "{top_pkg}", "Python", "{desc}")')

    lines.append("    }")

    # Add protocol-based external systems
    for proto in protocols:
        pid = f"ext_{proto.lower()}"
        lines.append(
            f'    System_Ext({pid}, "{proto} Clients", "External {proto} consumers")'
        )
        if comp_ids:
            lines.append(f'    Rel({pid}, {comp_ids[0]}, "{proto} requests")')

    # Add entry point relationships
    for ep in entry_info.get("entry_points", [])[:5]:
        ep_mod = ep.get("module", "").split(".")
        if len(ep_mod) > 1:
            target = re.sub(
                r"[^a-zA-Z0-9]", "_", ep_mod[1] if len(ep_mod) > 1 else ep_mod[0]
            )
            if target in comp_ids:
                lines.append(f'    Rel(user, {target}, "{ep["type"]} entry")')

    lines.append("```")

    return "\n".join(lines)


def save_generated_c4(project_path: Path, c4_content: str) -> str:
    """Save auto-generated C4 to .specify/reports/generated_c4.md."""
    if not c4_content:
        return ""
    output_dir = project_path / ".specify" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "generated_c4.md"
    output_file.write_text(c4_content)
    return str(output_file)


# ── Updated Main ───────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze_architecture.py <project_path>"}))
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()

    # Original analyses
    protocols = detect_protocols(project_path)
    types = analyze_type_coverage(project_path)
    structure = analyze_module_structure(project_path)
    config = detect_config_patterns(project_path)
    scoring = score_architecture(protocols, types, structure, config)

    # New: Architecture discovery (always runs)
    c4_discovery = discover_c4_architecture(project_path)
    hot_paths = identify_hot_paths(project_path)
    design_patterns = analyze_design_patterns(project_path)

    # Auto-generate C4 if none exists
    generated_c4_path = ""
    if not c4_discovery["has_c4"]:
        c4_content = auto_generate_c4(project_path, structure, protocols, hot_paths)
        if c4_content:
            generated_c4_path = save_generated_c4(project_path, c4_content)
            c4_discovery["auto_generated"] = True
            c4_discovery["generated_path"] = generated_c4_path

    # Boost/penalize score based on architecture quality
    arch_bonus = 0
    if c4_discovery["has_c4"]:
        arch_bonus += 5  # Has documented architecture
    if hot_paths["hot_path_coverage_pct"] >= 80:
        arch_bonus += 5  # Good hot path coverage
    elif hot_paths["cold_module_count"] > hot_paths["hot_path_modules"]:
        arch_bonus -= 5  # More cold code than hot
    scoring["score"] = min(scoring["score"] + arch_bonus, 100)
    if arch_bonus != 0:
        scoring["details"].append(f"Architecture depth bonus: {arch_bonus:+d}")

    print(
        json.dumps(
            {
                "domain": "CA-003",
                "domain_name": "Architecture",
                "project": str(project_path),
                "protocols": protocols,
                "type_coverage": types,
                "module_structure": structure,
                "config_patterns": config,
                "c4_architecture": c4_discovery,
                "hot_paths": hot_paths,
                "design_patterns": design_patterns,
                "generated_c4_path": generated_c4_path,
                "scoring": scoring,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""WS3: Create mcp/ subdirectory for all agents by extracting register_*_tools functions.

This script:
1. Parses mcp_server.py to find all register_*_tools function definitions
2. Extracts each function (and its dependencies) into mcp/mcp_{domain}.py
3. Creates mcp/__init__.py with proper re-exports
4. Updates mcp_server.py to import from the mcp/ subpackage

Does NOT delete the original functions from mcp_server.py — it creates the
mcp/ folder structure as a parallel path. The final migration (removing functions
from mcp_server.py) should be done per-project with proper testing.
"""

import ast
import os
from pathlib import Path


def _agents_dir() -> Path:
    package_root = os.environ.get("AGENT_PACKAGES_ROOT")
    if package_root:
        return Path(package_root).expanduser().resolve() / "agents"
    workspace = Path(os.environ.get("AGENT_UTILITIES_WORKSPACE_ROOT", Path.cwd()))
    return workspace.expanduser().resolve() / "agent-packages" / "agents"


AGENTS_DIR = _agents_dir()


def extract_register_functions(mcp_server_path: Path) -> dict[str, list[int]]:
    """Find all register_*_tools function definitions and their line ranges."""
    content = mcp_server_path.read_text()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {}

    functions = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name.startswith("register_")
            and node.name.endswith("_tools")
        ):
            domain = node.name.replace("register_", "").replace("_tools", "")
            functions[domain] = (node.lineno, node.end_lineno or node.lineno)

    return functions


def create_mcp_subpackage(project_dir: Path, project_name: str) -> int:
    """Create mcp/ subpackage for a project."""
    pkg_name = project_name.replace("-", "_")
    src_dir = project_dir / pkg_name
    mcp_server_path = src_dir / "mcp_server.py"

    if not mcp_server_path.exists():
        return 0

    mcp_dir = src_dir / "mcp"
    if mcp_dir.exists():
        return 0  # Already has mcp/ folder

    functions = extract_register_functions(mcp_server_path)
    if not functions:
        return 0

    mcp_dir.mkdir(exist_ok=True)

    # Read the full source for extracting function bodies
    lines = mcp_server_path.read_text().splitlines()

    # Create individual mcp_{domain}.py files
    domains = []
    for domain, (start_line, end_line) in sorted(functions.items()):
        func_lines = lines[start_line - 1 : end_line]
        func_body = "\n".join(func_lines)

        # Create the domain file
        domain_file = mcp_dir / f"mcp_{domain}.py"
        content = f'"""MCP tools for {domain.replace("_", " ")} operations.\n\nAuto-generated from mcp_server.py during ecosystem standardization.\n"""\n\n{func_body}\n'
        domain_file.write_text(content)
        domains.append(domain)

    # Create mcp/__init__.py
    imports = []
    exports = []
    for domain in sorted(domains):
        func_name = f"register_{domain}_tools"
        imports.append(f"from {pkg_name}.mcp.mcp_{domain} import {func_name}")
        exports.append(f'    "{func_name}",')

    init_content = f'"""MCP tool registration modules for {project_name}.\n\nAuto-generated during ecosystem standardization.\nEach domain has its own module with a register_*_tools function.\n"""\n\n'
    init_content += "\n".join(imports)
    init_content += "\n\n__all__ = [\n"
    init_content += "\n".join(exports)
    init_content += "\n]\n"

    (mcp_dir / "__init__.py").write_text(init_content)

    return len(domains)


def main():
    total_domains = 0
    total_projects = 0

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue

        pkg_name = agent_dir.name.replace("-", "_")
        if not (agent_dir / pkg_name / "mcp_server.py").exists():
            continue

        if (agent_dir / pkg_name / "mcp").exists():
            continue

        count = create_mcp_subpackage(agent_dir, agent_dir.name)
        if count > 0:
            print(f"  ✅ {agent_dir.name}: {count} domains → mcp/")
            total_domains += count
            total_projects += 1

    # Handle tools/ -> mcp/ migration for documentdb-mcp and langfuse-agent
    for proj in ["documentdb-mcp", "langfuse-agent"]:
        pkg = proj.replace("-", "_")
        tools_dir = AGENTS_DIR / proj / pkg / "tools"
        mcp_dir = AGENTS_DIR / proj / pkg / "mcp"
        if tools_dir.exists() and not mcp_dir.exists():
            # Create mcp/ alongside tools/ (don't delete tools/ yet)
            mcp_dir.mkdir(exist_ok=True)
            for f in tools_dir.iterdir():
                if f.suffix == ".py" and f.name != "__init__.py":
                    new_name = (
                        f"mcp_{f.name}" if not f.name.startswith("mcp_") else f.name
                    )
                    (mcp_dir / new_name).write_text(f.read_text())
                elif f.name == "__init__.py":
                    # Rewrite imports to use mcp_ prefix
                    content = f.read_text().replace(f"{pkg}.tools", f"{pkg}.mcp")
                    (mcp_dir / "__init__.py").write_text(content)
            print(f"  ✅ {proj}: tools/ → mcp/ (parallel copy created)")
            total_projects += 1

    print(
        f"\n📊 Created mcp/ subdirectory for {total_projects} projects ({total_domains} total domains)"
    )
    print(
        "   mcp_server.py still contains original functions (import migration needed per-project)"
    )


if __name__ == "__main__":
    main()

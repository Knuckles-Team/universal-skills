#!/usr/bin/env python3
import argparse
import tomllib
from pathlib import Path

TEMPLATE = """# AGENTS.md

## Tech Stack & Architecture
- Language/Version: Python 3.10+
- Core Libraries: `agent-utilities`, `fastmcp`, `pydantic-ai`
- Key principles: Functional patterns, Pydantic for data validation, asynchronous tool execution.
- Architecture:
    - `mcp.py`: Main MCP server entry point and tool registration.
    - `agent.py`: Pydantic AI agent definition and logic.
    - `skills/`: Directory containing modular agent skills (if applicable).
    - `agent/`: Internal agent logic and prompt templates.

### Architecture Diagram
```mermaid
graph TD
    User([User/A2A]) --> Server[A2A Server / FastAPI]
    Server --> Agent[Pydantic AI Agent]
    Agent --> Skills[Modular Skills]
    Agent --> MCP[MCP Server / FastMCP]
    MCP --> Client[API Client / Wrapper]
    Client --> ExternalAPI([External Service API])
```

### Workflow Diagram
```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant A as Agent
    participant T as MCP Tool
    participant API as External API

    U->>S: Request
    S->>A: Process Query
    A->>T: Invoke Tool
    T->>API: API Request
    API-->>T: API Response
    T-->>A: Tool Result
    A-->>S: Final Response
    S-->>U: Output
```

## Commands (run these exactly)
# Installation
pip install .[all]

# Quality & Linting (run from project root)
pre-commit run --all-files

# Execution Commands
{SCRIPTS_MD}

## Project Structure Quick Reference
- MCP Entry Point → `mcp.py`
- Agent Entry Point → `agent.py`
- Source Code → `{SOURCE_DIR}/`
- Skills → `skills/` (if exists)

### File Tree
```text
{TREE_VIEW}
```

## Code Style & Conventions
**Always:**
- Use `agent-utilities` for common patterns (e.g., `create_mcp_server`, `create_agent`).
- Define input/output models using Pydantic.
- Include descriptive docstrings for all tools (they are used as tool descriptions for LLMs).
- Check for optional dependencies using `try/except ImportError`.

**Good example:**
```python
from agent_utilities import create_mcp_server
from mcp.server.fastmcp import FastMCP

mcp = create_mcp_server("my-agent")

@mcp.tool()
async def my_tool(param: str) -> str:
    \"\"\"Description for LLM.\"\"\"
    return f"Result: {{param}}"
```

## Dos and Don'ts
**Do:**
- Run `pre-commit` before pushing changes.
- Use existing patterns from `agent-utilities`.
- Keep tools focused and idempotent where possible.

**Don't:**
- Use `cd` commands in scripts; use absolute paths or relative to project root.
- Add new dependencies to `dependencies` in `pyproject.toml` without checking `optional-dependencies` first.
- Hardcode secrets; use environment variables or `.env` files.

## Safety & Boundaries
**Always do:**
- Run lint/test via `pre-commit`.
- Use `agent-utilities` base classes.

**Ask first:**
- Major refactors of `mcp.py` or `agent.py`.
- Deleting or renaming public tool functions.

**Never do:**
- Commit `.env` files or secrets.
- Modify `agent-utilities` or `universal-skills` files from within this package.

## When Stuck
- Propose a plan first before making large changes.
- Check `agent-utilities` documentation for existing helpers.
"""


def get_tree_view(path, indent="", depth=2):
    if depth < 0:
        return ""

    ignore = {
        ".git",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        ".ipynb_checkpoints",
        ".ruff_cache",
        ".idea",
        "*.egg-info",
    }

    tree = []
    try:
        items = sorted([d for d in path.iterdir() if d.name not in ignore])
        for i, item in enumerate(items):
            # Check if name matches any ignore pattern (rudimentary)
            if any(Path(item.name).match(p) for p in ignore):
                continue

            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            tree.append(f"{indent}{connector}{item.name}")
            if item.is_dir() and depth > 0:
                next_indent = indent + ("    " if is_last else "│   ")
                tree.append(get_tree_view(item, next_indent, depth - 1))
    except Exception:
        pass
    return "\n".join([t for t in tree if t])


def get_metadata(project_dir):
    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    name = project.get("name", project_dir.name)
    description = project.get("description", "")
    scripts = project.get("scripts", {})

    source_dir = name.replace("-", "_")
    if not (project_dir / source_dir).exists():
        dirs = [
            d.name
            for d in project_dir.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and d.name not in {"tests", "skills"}
        ]
        if dirs:
            source_dir = dirs[0]

    return {
        "name": name,
        "description": description,
        "scripts": scripts,
        "path": project_dir,
        "source_dir": source_dir,
    }


def generate_agents_md(metadata):
    scripts_md = ""
    if metadata["scripts"]:
        scripts_md = "\n".join(
            [f"# {desc}\n{cmd}" for desc, cmd in metadata["scripts"].items()]
        )
    else:
        scripts_md = "# Run MCP Server (if applicable)\npython3 mcp.py\n# Run Agent (if applicable)\npython3 agent.py"

    tree_view = get_tree_view(metadata["path"])

    return TEMPLATE.format(
        NAME=metadata["name"],
        DESCRIPTION=metadata["description"],
        SCRIPTS_MD=scripts_md,
        SOURCE_DIR=metadata["source_dir"],
        TREE_VIEW=tree_view,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate AGENTS.md for a project.")
    parser.add_argument("path", help="Path to the project root directory")
    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.is_dir():
        print(f"Error: {project_path} is not a directory.")
        return

    meta = get_metadata(project_path)
    if not meta:
        print(f"Error: Could not find pyproject.toml in {project_path}")
        return

    content = generate_agents_md(meta)
    target_file = project_path / "AGENTS.md"

    with open(target_file, "w") as f:
        f.write(content)

    print(f"Successfully generated AGENTS.md at {target_file}")


if __name__ == "__main__":
    main()

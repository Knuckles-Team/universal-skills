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
    - `mcp_server.py`: Main MCP server entry point and tool registration.
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
- MCP Entry Point → `mcp_server.py`
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
- Major refactors of `mcp_server.py` or `agent.py`.
- Deleting or renaming public tool functions.

**Never do:**
- Commit `.env` files or secrets.
- Modify `agent-utilities` or `universal-skills` files from within this package.

## When Stuck
- Propose a plan first before making large changes.
- Check `agent-utilities` documentation for existing helpers.

## Working Discipline — think, simplify, stay surgical, verify

These four habits cut the most common LLM coding mistakes. For trivial tasks, use
judgment; the bias here is correctness over speed.

- **Think before coding.** State your assumptions explicitly. If a request has more than
  one reasonable reading, surface the options instead of silently picking one. If a
  simpler approach exists, say so and push back when warranted. When something is
  genuinely unclear, stop and name what's confusing — ask, don't guess.
- **Simplicity first.** Write the minimum code that solves the stated problem — no
  speculative features, no abstraction for single-use code, no configurability that
  wasn't requested, no error handling for impossible states. If you wrote 200 lines and
  it could be 50, rewrite it. (Name code from its purpose, never `wave0`/`phase2`/`v2`.)
- **Stay surgical.** Every changed line should trace directly to the task. Don't refactor,
  reformat, or "improve" working code adjacent to your change; match the existing style
  even where you'd do it differently. Remove only the imports/symbols your own change
  orphaned; if you spot unrelated dead code, mention it rather than deleting it inline.
  *Exception — the Quality Bar below:* lint/format/type errors the pre-commit gate flags
  get fixed regardless of who introduced them. In short: **surgical on behavior, clean on
  lint.**
- **Verify against a goal.** Turn the task into a checkable outcome before you start:
  "fix the bug" → "write a failing test that reproduces it, then make it pass"; "add
  validation" → "tests for the invalid inputs pass". For multi-step work, state the short
  plan and the check for each step, then loop until the checks pass.

## Quality Bar — Leave the Codebase Clean (REQUIRED)

After completing any code change, run the project's pre-commit suite and drive it
**fully green** before committing:

```bash
pre-commit run --all-files
```

Resolve **every** issue it reports — failures, lint errors, type errors, and
warnings — **including problems that pre-date your change and were not caused by
your edits**. The standing goal is a clean, working codebase with **no errors and
no warnings**. Do not silence checks (`# noqa`, `# type: ignore`, `SKIP=`,
`--no-verify`) to force green unless the exception is already documented in this
file as a known, unavoidable limitation. Only commit once `pre-commit run
--all-files` passes cleanly; if a check legitimately cannot pass, stop and explain
why rather than bypassing it.

## Working with Git Worktrees (multi-session)

Multiple agents/sessions work the `agent-packages/*` repos concurrently. **Do not
edit the canonical checkout** (`/home/apps/workspace/agent-packages/<repo>`) — a
background `repository-manager` sync can reset its working tree and discard
uncommitted edits. Take your own git worktree on your own branch instead:

```bash
# preferred — repository-manager MCP:
rm_worktree add <repo> <your-branch>      # -> /home/apps/worktrees/<repo>/<your-branch>

# raw-git fallback:
git -C agent-packages/<repo> checkout main
git -C agent-packages/<repo> worktree add /home/apps/worktrees/<repo>/<branch> -b <branch>
```

Work in the worktree and **commit often** (commits survive a working-tree reset).
Each session must use a **distinct branch** — git allows a branch in only one
worktree, which is what keeps concurrent sessions from colliding. Worktrees live
under `/home/apps/worktrees/` (outside the workspace scan, so the sync leaves them
alone).

**Finishing work in a worktree** — run this sequence before calling it done:
1. **Pre-commit green** — `pre-commit run --all-files`; resolve every issue per the
   Quality Bar above (including pre-existing), no `--no-verify`.
2. **Commit** in the worktree.
3. **Merge to main locally** — `rm_worktree merge <repo> <branch> --into main`
   (or `git merge --no-ff`). Push only when the user asks.
4. **Clean up** — remove the worktree and delete the merged branch:
   `rm_worktree remove <repo> <branch> --delete-branch`; `rm_worktree prune` clears
   stale entries. (Raw-git: `git worktree remove <path> && git branch -d <branch>`.)
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
        scripts_md = "# Run MCP Server (if applicable)\npython3 mcp_server.py\n# Run Agent (if applicable)\npython3 agent.py"

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

---
name: agents-md-generator
domain: agent-tools
skill_type: skill
description: >-
  Generate or update a robust AGENTS.md file (the "README for AI coding agents")
  for a project. This skill ensures your repository is optimized for AI tools
  (like Copilot, Cursor, and Windsurf) by providing structured context, commands,
  architecture diagrams, and coding standards. It automatically detects project
  metadata from pyproject.toml and generates a project tree view.
license: MIT
tags: [agent, agents.md, documentation, ai-optimization, mcp, architecture]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# AGENTS.md Generator

Generates a robust `AGENTS.md` file designed specifically for AI coding agents. This file acts as a "README for machines," providing them with the exact project context, rules, and instructions they need to work effectively.

## Features
- **Project Metadata Extraction**: Automatically parses `pyproject.toml` for project name, description, and scripts.
- **Dynamic File Tree**: Generates a text-based tree view of the project structure, ignoring common noise directories (`.git`, `__pycache__`, etc.).
- **Mermaid Diagrams**: Includes standardized Architecture and Workflow diagrams to help agents understand the system's design.
- **Battle-Tested Template**: Uses a structure optimized for high agent performance, including "Always/Ask first/Never" boundaries.

## Usage

Run the generator script with the path to your project root:

```bash
python scripts/generate_agents_md.py <project-path>
```

### Options
- `<project-path>`: (Required) Path to the root directory of the project to document.

## Steps

1. Confirm the target is a project root with `ls <project-path>/pyproject.toml`. Verify that the file is listed, since metadata extraction reads it.
2. Generate the file with `python scripts/generate_agents_md.py <project-path>`. Verify that the command exits 0 and prints no traceback.
3. Inspect the result with `grep -n "^## " <project-path>/AGENTS.md`. Verify that the sections from the AGENTS.md Standard below (commands, structure, boundaries, When Stuck) are present.
4. Review the file tree and commands by reading `<project-path>/AGENTS.md`. Verify that the project name matches `pyproject.toml` and that no noise directories such as `.git` or `__pycache__` appear.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `FileNotFoundError` for `pyproject.toml` | Path is not a Python project root | Pass the directory that contains `pyproject.toml`, or add a minimal one before re-running the script. |
| Existing AGENTS.md content lost | Script rewrote the file | Restore it with `git checkout -- AGENTS.md` and merge by hand, or generate into a copy first. |
| Tree view is huge or noisy | Generated or vendored directories in the project | Delete or ignore the directories in the project, then regenerate. |

## AGENTS.md Standard

The generated `AGENTS.md` follows the emerging open standard for AI agent documentation:
1. **Tech Stack & Architecture**: High-level overview of technologies and component interactions.
2. **Commands**: Exact, file-scoped commands for building, testing, and linting.
3. **Project Structure**: Quick reference to key files and the dynamic tree view.
4. **Code Style & Conventions**: Specific "Always" rules with concrete Good/Bad code examples.
5. **Dos and Don'ts**: Specific behavioral guidelines.
6. **Safety & Boundaries**: Explicit "Always do", "Ask first", and "Never do" constraints.
7. **When Stuck**: Instructions on how to handle ambiguity (e.g., "propose a plan first").

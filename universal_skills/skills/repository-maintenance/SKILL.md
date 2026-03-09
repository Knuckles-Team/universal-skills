---
name: repository-maintenance
description: Guide for bulk repository maintenance, including parallel pre-commit checks and phased version bumping using `repository-manager`. Use when updating multiple interdependent packages or performing fleet-wide CI/CD health checks.
license: MIT
tags: [maintenance, git, pre-commit, bump2version, parallel, automation]
metadata:
  author: Antigravity
  version: '0.1.0'
---
# Repository Maintenance & Phased Bumping

## Overview

Comprehensive guide for managing a fleet of repositories. This skill leverages `repository-manager` to perform parallel Git and CI operations, and implements the **Phased Bumping** pattern for safe, interdependent package updates.

---

## 1. `repository-manager` — Fleet Management CLI

The `repository-manager` (RM) tool is the primary CLI for bulk operations.

### Parallel Pre-commit Checks
Run pre-commit hooks across all projects in the workspace simultaneously. RM automatically skips the `no-commit-to-branch` hook to prevent maintenance-run failures.

```bash
# Run pre-commit on all repositories
repository-manager --workspace ~/Workspace/agent-packages --pre-commit
```

### Bulk Version Bumping
Bump the version (patch, minor, major) for all repositories in a workspace that contain a `.bumpversion.cfg`.

```bash
# Bump all to the next patch version
repository-manager --workspace ~/Workspace/agent-packages --bump patch
```

### Extended Capabilities (MCP & A2A)

`repository-manager` is not just a CLI tool; it also acts as a bridge for Agentic AI:

- **MCP Server**: Can be run as a Model Context Protocol (MCP) server, allowing AI agents to perform Git operations, search codebases, and edit files using a standardized toolset.
- **A2A (Agent-to-Agent)**: Supports an Agent-to-Agent communication layer via FastAPI, enabling specialized agents to coordinate repository tasks.
- **Smart Coding Integration**: Automatically configures `smart-coding-mcp` for any Git projects found in a workspace, enabling semantic search and codebase intelligence.

```bash
# Start RM as an MCP server
repository-manager-mcp --transport stdio
```

---

## 2. Phased Maintenance Workflow

When managing interdependent packages (e.g., a library and its consumers), updates MUST happen in a specific order to ensure dependency constraints stay valid.

### The Phased Bumping Pattern
RM implements a 5-phase maintenance workflow:

1.  **Phase 1 (Core Skills)**: Update base skills (e.g., `universal-skills`).
2.  **Phase 2 (Graphs/Templates)**: Update downstream templates (e.g., `skill-graphs`).
3.  **Phase 3 (UI/Consumables)**: Update frontend/UI packages.
4.  **Phase 4 (Core Utilities)**: Update the main utility library (e.g., `agent-utilities`) and propagate new versions of Phase 1-3 to it.
5.  **Phase 5 (General Packages)**: Update all remaining packages and propagate the new `agent-utilities` version to them.

### Running Maintenance
```bash
# Run full maintenance (pre-commit + phased bumping)
repository-manager --workspace ~/Workspace/agent-packages --maintain

# Start at a specific phase (e.g., resume at Phase 4 after a fix)
repository-manager --workspace ~/Workspace/agent-packages --maintain --phase 4

# Dry run to preview changes
repository-manager --workspace ~/Workspace/agent-packages --maintain --dry-run
```

---

## 3. Configurable Phased Maintenance

You can define custom maintenance workflows by providing a JSON configuration file. This allows you to skip specific projects or create entirely different phasing logic.

### Full Default Configuration (`maintenance_config.json`)
This is the internal default configuration used by `repository-manager`. You can copy this to a file and customize it for your specific fleet requirements.

```json
{
    "phases": [
        {
            "name": "Phase 1 - universal-skills",
            "phase": 1,
            "project": "universal-skills",
            "updates": [
                {
                    "target": "agent-utilities/pyproject.toml",
                    "package": "universal-skills"
                }
            ]
        },
        {
            "name": "Phase 2 - skill-graphs",
            "phase": 2,
            "project": "skill-graphs",
            "updates": [
                {
                    "target": "agent-utilities/pyproject.toml",
                    "package": "skill-graphs"
                }
            ]
        },
        {
            "name": "Phase 3 - agent-webui",
            "phase": 3,
            "project": "agent-webui",
            "updates": [
                {
                    "target": "agent-utilities/pyproject.toml",
                    "package": "agent-webui"
                }
            ]
        },
        {
            "name": "Phase 4 - agent-utilities",
            "phase": 4,
            "project": "agent-utilities",
            "updates": [
                {
                    "target_pattern": "*",
                    "exclude": [
                        "universal-skills",
                        "agent-utilities",
                        "agent-webui"
                    ],
                    "package": "agent-utilities"
                }
            ]
        },
        {
            "name": "Phase 5 - Rest of packages",
            "phase": 5,
            "bulk_bump": true,
            "exclude": [
                "universal-skills",
                "agent-utilities",
                "agent-webui"
            ]
        }
    ]
}
```

### CLI Usage Examples

#### Dry Run (Preview Changes)
Always perform a dry run when using a new configuration to verify the impact.
```bash
repository-manager --workspace ~/Workspace/agent-packages --maintain --config maintenance_config.json --dry-run
```

#### Live Maintenance (Apply Changes)
Execute the maintenance cycle and apply version bumps and dependency updates.
```bash
repository-manager --workspace ~/Workspace/agent-packages --maintain --config maintenance_config.json
```

---

## 4. Best Practices

- **Always Dry Run First**: Use `--dry-run` to verify which files will be modified and what the new versions will be.
- **Skip Pre-commit if Already Verified**: If you just ran pre-commits, use `--skip-pre-commit` to speed up the bumping process.
- **Phased Recovery**: If maintenance fails at Phase 3, fix the issue and restart with `--phase 3` to avoid redundant bumps in Phase 1 & 2.
- **Sync Dependencies**: After bumping a core library, ensure all downstream `pyproject.toml` files are updated to require the new version. `repository-manager` handles this automatically during the `--maintain` workflow.

---

## 5. Troubleshooting

- **No .bumpversion.cfg**: If a project is skipped during bumping, ensure it has a valid `.bumpversion.cfg` and a clear `current_version` defined.
- **Pre-commit Failures**: Check the logs in RM's output. Common failures are often due to local environment mismatches; ensure `pre-commit` is installed and the environment is clean.
- **Dependency Conflicts**: If a phase fails due to a dependency version mismatch, check the `pyproject.toml` of the failing package and ensure it uses the `>=` operator for internal dependencies.

---
name: workspace_inventory
description: >-
  Full workspace discovery — list available workspace actions, repositories, and validate project structure.
domain: dev-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
tags: ['workspace', 'git', 'validation', 'repositories']
concept: CONCEPT:DEV-001
---

# Workspace Inventory Workflow

**CONCEPT:DEV-001**

Full workspace discovery — list available workspace actions, repositories, and validate project structure.

## Steps

### Step 0: Repository Manager Mcp
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Use the rm_workspace tool to list the available actions for the workspace
Expected: `list, setup`

### Step 1: Repository Manager Mcp
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

List all managed repositories in the workspace with their status
Expected: `repository`

### Step 2: KG Persistence [depends_on: repository-manager-mcp]
**Agent**: `builder-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Workspace Inventory results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Repository Manager Mcp; Step 1 — Repository Manager Mcp
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

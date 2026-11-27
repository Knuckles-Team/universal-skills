---
name: workspace-inventory
skill_type: workflow
description: >-
  Full workspace discovery — list available workspace actions, repositories, and validate project structure.
domain: development-workflows
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
metadata:
  version: '1.7.0'
---

# Workspace Inventory Workflow

**CONCEPT:DEV-001**

Full workspace discovery — list available workspace actions, repositories, and validate project structure.

## Steps

1. List workspace actions with the `rm_workspace_*` tools. Verify that the action list is returned.
2. List managed repositories using the `rep_rm_projects` tools. Verify that each repository is listed with a status.
3. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: list-workspace-actions [skill: repository-manager-mcp]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Use the `rm_workspace_*` tools (one per workspace operation) for the workspace
Expected: `list, setup`

### Step 1: list-managed-repositories [skill: repository-manager-mcp]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

List all managed repositories in the workspace with their status
Expected: `repository`

### Step 2: KG Persistence [depends_on: Step 0, Step 1]
**Agent**: `builder-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Repository list is empty | Workspace not set up | Run the workspace setup action via `rm_workspace_*` and list again. |
| A repository shows missing | Checkout absent | Clone it with the repository-manager clone action and list again. |
| Tools unavailable | `repository-manager-mcp` not connected | Start the MCP server and reconnect, and call the tool again. |

## Output
- Workspace Inventory results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — list-workspace-actions; Step 1 — list-managed-repositories
- **After level 0:** Step 2 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

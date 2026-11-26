---
name: workspace-health-check
skill_type: workflow
description: >-
  Combined workspace + system health validation. Checks repository state alongside system resources.
domain: development-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
    - validator-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: ['workspace', 'health', 'systems', 'cross-domain']
concept: CONCEPT:DEV-001
metadata:
  version: '1.6.2'
---

# Workspace Health Check Workflow

**CONCEPT:DEV-001**

Combined workspace + system health validation. Checks repository state alongside system resources.

## Steps

1. List workspace actions and configuration with the `rep_rm_workspace` tools. Verify that the action list is returned.
2. Read memory and CPU with the `systems-manager` tools. Verify that both values are present.
3. Check disk usage of the workspace partition with `df -h <workspace-path>`. Verify that a usage percentage is reported.
4. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: Repository Manager Mcp
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

List the available workspace actions and current workspace configuration
Expected: `workspace, list`

### Step 1: collect-system-utilization [skill: systems-manager]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Get current system memory and CPU utilization
Expected: `memory, cpu`

### Step 2: collect-disk-usage [skill: systems-manager]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Check disk usage for the main workspace partition
Expected: `disk, usage`

### Step 3: KG Persistence [depends_on: Step 1, Step 2]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Workspace tools return empty | Workspace config missing | Run the workspace setup action from `rep_rm_workspace` and list again. |
| Disk is almost full | Build artifacts accumulate | Remove caches and old venvs, and re-check with `df -h`. |
| System stats fail | Host not reachable | Check connectivity and re-run the systems-manager call. |

## Output
- Workspace Health Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Repository Manager Mcp; Step 1 — collect-system-utilization; Step 2 — collect-disk-usage
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

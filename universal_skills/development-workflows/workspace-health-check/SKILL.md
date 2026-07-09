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
  version: '1.1.0'
---

# Workspace Health Check Workflow

**CONCEPT:DEV-001**

Combined workspace + system health validation. Checks repository state alongside system resources.

## Steps

### Step 0: Repository Manager Mcp
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

List the available workspace actions and current workspace configuration
Expected: `workspace, list`

### Step 1: Systems Manager
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Get current system memory and CPU utilization
Expected: `memory, cpu`

### Step 2: Systems Manager
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Check disk usage for the main workspace partition
Expected: `disk, usage`

### Step 3: KG Persistence [depends_on: systems-manager]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Workspace Health Check results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Repository Manager Mcp; Step 1 — Systems Manager; Step 2 — Systems Manager
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

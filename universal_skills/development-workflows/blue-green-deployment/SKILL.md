---
name: blue-green-deployment
skill_type: workflow
description: >-
  Parallel execution workflow for blue green deployment using the Unified Parallel Engine
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
    - publisher-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
    publisher-agent: [rep_rm_git, gl_merge_requests]
tags: [dev-workflows, blue-green-deployment]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# Blue Green Deployment Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for blue green deployment using the Unified Parallel Engine

## Steps

### Step 1: Deploy Green
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute deploy green operations for the Blue Green Deployment workflow.
Expected: `deploy_green_artifacts`

### Step 2: Health Check [depends_on: deploy_green]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute health check operations for the Blue Green Deployment workflow.
Expected: `health_check_artifacts`

### Step 3: Switch Traffic [depends_on: health_check]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute switch traffic operations for the Blue Green Deployment workflow.
Expected: `switch_traffic_artifacts`

### Step 4: Drain Blue [depends_on: switch_traffic]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute drain blue operations for the Blue Green Deployment workflow.
Expected: `drain_blue_artifacts`

### Step 5: KG Persistence [depends_on: drain_blue]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Blue Green Deployment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Deploy Green
- **After level 0:** Step 2 — Health Check
- **After level 1:** Step 3 — Switch Traffic
- **After level 2:** Step 4 — Drain Blue
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

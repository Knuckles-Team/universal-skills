---
name: canary-deployment
skill_type: workflow
description: >-
  Parallel execution workflow for canary deployment using the Unified Parallel Engine
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
tags: [dev-workflows, canary-deployment]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Canary Deployment Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for canary deployment using the Unified Parallel Engine

## Steps

### Step 1: Deploy Canary
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute deploy canary operations for the Canary Deployment workflow.
Expected: `deploy_canary_artifacts`

### Step 2: Monitor Metrics [depends_on: deploy_canary]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute monitor metrics operations for the Canary Deployment workflow.
Expected: `monitor_metrics_artifacts`

### Step 3: Compare To Baseline [depends_on: monitor_metrics]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute compare to baseline operations for the Canary Deployment workflow.
Expected: `compare_to_baseline_artifacts`

### Step 4: Promote Rollback [depends_on: compare_to_baseline]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute promote rollback operations for the Canary Deployment workflow.
Expected: `promote_rollback_artifacts`

### Step 5: KG Persistence [depends_on: promote_rollback]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Canary Deployment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Deploy Canary
- **After level 0:** Step 2 — Monitor Metrics
- **After level 1:** Step 3 — Compare To Baseline
- **After level 2:** Step 4 — Promote Rollback
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

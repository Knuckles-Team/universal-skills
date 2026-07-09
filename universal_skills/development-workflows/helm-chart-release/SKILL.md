---
name: helm-chart-release
skill_type: workflow
description: >-
  Parallel execution workflow for helm chart release using the Unified Parallel Engine
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
tags: [dev-workflows, helm-chart-release]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Helm Chart Release Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for helm chart release using the Unified Parallel Engine

## Steps

### Step 1: Lint
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute lint operations for the Helm Chart Release workflow.
Expected: `lint_artifacts`

### Step 2: Template [depends_on: lint]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute template operations for the Helm Chart Release workflow.
Expected: `template_artifacts`

### Step 3: Package [depends_on: template]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute package operations for the Helm Chart Release workflow.
Expected: `package_artifacts`

### Step 4: Push [depends_on: package]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute push operations for the Helm Chart Release workflow.
Expected: `push_artifacts`

### Step 5: Deploy [depends_on: push]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute deploy operations for the Helm Chart Release workflow.
Expected: `deploy_artifacts`

### Step 6: Verify [depends_on: deploy]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute verify operations for the Helm Chart Release workflow.
Expected: `verify_artifacts`

### Step 7: KG Persistence [depends_on: verify]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Helm Chart Release results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Lint
- **After level 0:** Step 2 — Template
- **After level 1:** Step 3 — Package
- **After level 2:** Step 4 — Push
- **After level 3:** Step 5 — Deploy
- **After level 4:** Step 6 — Verify
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

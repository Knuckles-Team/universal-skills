---
name: pre-commit-standardization
skill_type: workflow
description: >-
  Parallel execution workflow for pre commit standardization using the Unified Parallel Engine
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
tags: [dev-workflows, pre-commit-standardization]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Pre Commit Standardization Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for pre commit standardization using the Unified Parallel Engine

## Steps

### Step 1: Check Config
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute check config operations for the Pre Commit Standardization workflow.
Expected: `check_config_artifacts`

### Step 2: Update Hooks [depends_on: check_config]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute update hooks operations for the Pre Commit Standardization workflow.
Expected: `update_hooks_artifacts`

### Step 3: Run [depends_on: update_hooks]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute run operations for the Pre Commit Standardization workflow.
Expected: `run_artifacts`

### Step 4: Fix [depends_on: run]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute fix operations for the Pre Commit Standardization workflow.
Expected: `fix_artifacts`

### Step 5: Commit [depends_on: fix]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute commit operations for the Pre Commit Standardization workflow.
Expected: `commit_artifacts`

### Step 6: KG Persistence [depends_on: commit]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Pre Commit Standardization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Check Config
- **After level 0:** Step 2 — Update Hooks
- **After level 1:** Step 3 — Run
- **After level 2:** Step 4 — Fix
- **After level 3:** Step 5 — Commit
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

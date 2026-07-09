---
name: rollback-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for rollback pipeline using the Unified Parallel Engine
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
tags: [dev-workflows, rollback-pipeline]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# Rollback Pipeline Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for rollback pipeline using the Unified Parallel Engine

## Steps

### Step 1: Detect Failure
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute detect failure operations for the Rollback Pipeline workflow.
Expected: `detect_failure_artifacts`

### Step 2: Identify Last Good [depends_on: detect_failure]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute identify last good operations for the Rollback Pipeline workflow.
Expected: `identify_last_good_artifacts`

### Step 3: Revert [depends_on: identify_last_good]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute revert operations for the Rollback Pipeline workflow.
Expected: `revert_artifacts`

### Step 4: Verify [depends_on: revert]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute verify operations for the Rollback Pipeline workflow.
Expected: `verify_artifacts`

### Step 5: Notify [depends_on: verify]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute notify operations for the Rollback Pipeline workflow.
Expected: `notify_artifacts`

### Step 6: KG Persistence [depends_on: notify]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Rollback Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Failure
- **After level 0:** Step 2 — Identify Last Good
- **After level 1:** Step 3 — Revert
- **After level 2:** Step 4 — Verify
- **After level 3:** Step 5 — Notify
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

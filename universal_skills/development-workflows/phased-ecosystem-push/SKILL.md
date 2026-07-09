---
name: phased-ecosystem-push
description: >-
  Parallel execution workflow for phased ecosystem push using the Unified Parallel Engine
domain: dev-workflows
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
tags: [dev-workflows, phased-ecosystem-push]
concept: CONCEPT:DEV-001
---

# Phased Ecosystem Push Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for phased ecosystem push using the Unified Parallel Engine

## Steps

### Step 1: Wave Per Phase Bump
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute wave per phase bump operations for the Phased Ecosystem Push workflow.
Expected: `wave_per_phase_bump_artifacts`

### Step 2: Commit [depends_on: wave_per_phase_bump]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute commit operations for the Phased Ecosystem Push workflow.
Expected: `commit_artifacts`

### Step 3: Push [depends_on: commit]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute push operations for the Phased Ecosystem Push workflow.
Expected: `push_artifacts`

### Step 4: Verify Ci [depends_on: push]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute verify ci operations for the Phased Ecosystem Push workflow.
Expected: `verify_ci_artifacts`

### Step 5: Next Phase [depends_on: verify_ci]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute next phase operations for the Phased Ecosystem Push workflow.
Expected: `next_phase_artifacts`

### Step 6: KG Persistence [depends_on: next_phase]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Phased Ecosystem Push results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Wave Per Phase Bump
- **After level 0:** Step 2 — Commit
- **After level 1:** Step 3 — Push
- **After level 2:** Step 4 — Verify Ci
- **After level 3:** Step 5 — Next Phase
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

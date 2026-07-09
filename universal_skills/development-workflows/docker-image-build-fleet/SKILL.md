---
name: docker-image-build-fleet
description: >-
  Parallel execution workflow for docker image build fleet using the Unified Parallel Engine
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
tags: [dev-workflows, docker-image-build-fleet]
concept: CONCEPT:DEV-001
---

# Docker Image Build Fleet Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for docker image build fleet using the Unified Parallel Engine

## Steps

### Step 1: Build
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute build operations for the Docker Image Build Fleet workflow.
Expected: `build_artifacts`

### Step 2: Scan [depends_on: build]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute scan operations for the Docker Image Build Fleet workflow.
Expected: `scan_artifacts`

### Step 3: Push [depends_on: scan]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute push operations for the Docker Image Build Fleet workflow.
Expected: `push_artifacts`

### Step 4: Update Stack [depends_on: push]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute update stack operations for the Docker Image Build Fleet workflow.
Expected: `update_stack_artifacts`

### Step 5: KG Persistence [depends_on: update_stack]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Docker Image Build Fleet results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Build
- **After level 0:** Step 2 — Scan
- **After level 1:** Step 3 — Push
- **After level 2:** Step 4 — Update Stack
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

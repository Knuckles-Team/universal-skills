---
name: api-breaking-change-migration
skill_type: workflow
description: >-
  Parallel execution workflow for api breaking change migration using the Unified Parallel Engine
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
tags: [dev-workflows, api-breaking-change-migration]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Api Breaking Change Migration Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for api breaking change migration using the Unified Parallel Engine

## Steps

### Step 1: Detect Breaking Changes
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute detect breaking changes operations for the Api Breaking Change Migration workflow.
Expected: `detect_breaking_changes_artifacts`

### Step 2: Find All Consumers [depends_on: detect_breaking_changes]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute find all consumers operations for the Api Breaking Change Migration workflow.
Expected: `find_all_consumers_artifacts`

### Step 3: Parallel Update [depends_on: find_all_consumers]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute parallel update operations for the Api Breaking Change Migration workflow.
Expected: `parallel_update_artifacts`

### Step 4: Test [depends_on: parallel_update]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute test operations for the Api Breaking Change Migration workflow.
Expected: `test_artifacts`

### Step 5: KG Persistence [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Api Breaking Change Migration results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Breaking Changes
- **After level 0:** Step 2 — Find All Consumers
- **After level 1:** Step 3 — Parallel Update
- **After level 2:** Step 4 — Test
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

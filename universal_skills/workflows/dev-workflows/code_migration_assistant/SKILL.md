---
name: code_migration_assistant
description: >-
  Parallel execution workflow for code migration assistant using the Unified Parallel Engine
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
tags: [dev-workflows, code-migration-assistant]
concept: CONCEPT:DEV-001
---

# Code Migration Assistant Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for code migration assistant using the Unified Parallel Engine

## Steps

### Step 1: Analyze Source
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute analyze source operations for the Code Migration Assistant workflow.
Expected: `analyze_source_artifacts`

### Step 2: Plan Migration [depends_on: analyze_source]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute plan migration operations for the Code Migration Assistant workflow.
Expected: `plan_migration_artifacts`

### Step 3: Parallel Convert [depends_on: plan_migration]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute parallel convert operations for the Code Migration Assistant workflow.
Expected: `parallel_convert_artifacts`

### Step 4: Test [depends_on: parallel_convert]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute test operations for the Code Migration Assistant workflow.
Expected: `test_artifacts`

### Step 5: Validate [depends_on: test]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute validate operations for the Code Migration Assistant workflow.
Expected: `validate_artifacts`

### Step 6: KG Persistence [depends_on: validate]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Code Migration Assistant results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Analyze Source
- **After level 0:** Step 2 — Plan Migration
- **After level 1:** Step 3 — Parallel Convert
- **After level 2:** Step 4 — Test
- **After level 3:** Step 5 — Validate
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

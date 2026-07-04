---
name: error_handling_audit
description: >-
  Parallel execution workflow for error handling audit using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: [dev-workflows, error-handling-audit]
concept: CONCEPT:DEV-001
---

# Error Handling Audit Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for error handling audit using the Unified Parallel Engine

## Steps

### Step 1: Find Bare Except
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute find bare except operations for the Error Handling Audit workflow.
Expected: `find_bare_except_artifacts`

### Step 2: Add Specific Handlers [depends_on: find_bare_except]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute add specific handlers operations for the Error Handling Audit workflow.
Expected: `add_specific_handlers_artifacts`

### Step 3: Test [depends_on: add_specific_handlers]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Error Handling Audit workflow.
Expected: `test_artifacts`

### Step 4: KG Persistence [depends_on: test]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Error Handling Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Find Bare Except
- **After level 0:** Step 2 — Add Specific Handlers
- **After level 1:** Step 3 — Test
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: type-coverage-campaign
skill_type: workflow
description: >-
  Parallel execution workflow for type coverage campaign using the Unified Parallel Engine
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
tags: [dev-workflows, type-coverage-campaign]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Type Coverage Campaign Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for type coverage campaign using the Unified Parallel Engine

## Steps

### Step 1: Pyright Mypy Analysis
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute pyright mypy analysis operations for the Type Coverage Campaign workflow.
Expected: `pyright_mypy_analysis_artifacts`

### Step 2: Add Types [depends_on: pyright_mypy_analysis]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute add types operations for the Type Coverage Campaign workflow.
Expected: `add_types_artifacts`

### Step 3: Test [depends_on: add_types]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Type Coverage Campaign workflow.
Expected: `test_artifacts`

### Step 4: Pr [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Type Coverage Campaign workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Type Coverage Campaign results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Pyright Mypy Analysis
- **After level 0:** Step 2 — Add Types
- **After level 1:** Step 3 — Test
- **After level 2:** Step 4 — Pr
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: dead_code_elimination
description: >-
  Parallel execution workflow for dead code elimination using the Unified Parallel Engine
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
tags: [dev-workflows, dead-code-elimination]
concept: CONCEPT:DEV-001
---

# Dead Code Elimination Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for dead code elimination using the Unified Parallel Engine

## Steps

### Step 1: Ast Analysis
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute ast analysis operations for the Dead Code Elimination workflow.
Expected: `ast_analysis_artifacts`

### Step 2: Unused Imports [depends_on: ast_analysis]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute unused imports operations for the Dead Code Elimination workflow.
Expected: `unused_imports_artifacts`

### Step 3: Unreachable Code [depends_on: unused_imports]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute unreachable code operations for the Dead Code Elimination workflow.
Expected: `unreachable_code_artifacts`

### Step 4: Pr [depends_on: unreachable_code]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Dead Code Elimination workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dead Code Elimination results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Ast Analysis
- **After level 0:** Step 2 — Unused Imports
- **After level 1:** Step 3 — Unreachable Code
- **After level 2:** Step 4 — Pr
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

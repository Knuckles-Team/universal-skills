---
name: technical-debt-sprint
skill_type: workflow
description: >-
  Parallel execution workflow for technical debt sprint using the Unified Parallel Engine
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
tags: [dev-workflows, technical-debt-sprint]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Technical Debt Sprint Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for technical debt sprint using the Unified Parallel Engine

## Steps

### Step 1: Lint Fixes
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute lint fixes operations for the Technical Debt Sprint workflow.
Expected: `lint_fixes_artifacts`

### Step 2: Dead Code
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute dead code operations for the Technical Debt Sprint workflow.
Expected: `dead_code_artifacts`

### Step 3: Type Coverage
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute type coverage operations for the Technical Debt Sprint workflow.
Expected: `type_coverage_artifacts`

### Step 4: Doc Gaps
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute doc gaps operations for the Technical Debt Sprint workflow.
Expected: `doc_gaps_artifacts`

### Step 5: Parallel Prs [depends_on: lint_fixes, dead_code, type_coverage, doc_gaps]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute parallel prs operations for the Technical Debt Sprint workflow.
Expected: `parallel_prs_artifacts`

### Step 6: KG Persistence [depends_on: parallel_prs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Technical Debt Sprint results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Lint Fixes; Step 2 — Dead Code; Step 3 — Type Coverage; Step 4 — Doc Gaps
- **After level 0:** Step 5 — Parallel Prs
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

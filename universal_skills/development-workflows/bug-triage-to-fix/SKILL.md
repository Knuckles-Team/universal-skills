---
name: bug-triage-to-fix
skill_type: workflow
description: >-
  Parallel execution workflow for bug triage to fix using the Unified Parallel Engine
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
tags: [dev-workflows, bug-triage-to-fix]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Bug Triage To Fix Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for bug triage to fix using the Unified Parallel Engine

## Steps

### Step 1: Triage
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute triage operations for the Bug Triage To Fix workflow.
Expected: `triage_artifacts`

### Step 2: Reproduce [depends_on: triage]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute reproduce operations for the Bug Triage To Fix workflow.
Expected: `reproduce_artifacts`

### Step 3: Diagnose [depends_on: reproduce]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute diagnose operations for the Bug Triage To Fix workflow.
Expected: `diagnose_artifacts`

### Step 4: Fix [depends_on: diagnose]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute fix operations for the Bug Triage To Fix workflow.
Expected: `fix_artifacts`

### Step 5: Test [depends_on: fix]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute test operations for the Bug Triage To Fix workflow.
Expected: `test_artifacts`

### Step 6: Pr [depends_on: test]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute pr operations for the Bug Triage To Fix workflow.
Expected: `pr_artifacts`

### Step 7: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Bug Triage To Fix results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Triage
- **After level 0:** Step 2 — Reproduce
- **After level 1:** Step 3 — Diagnose
- **After level 2:** Step 4 — Fix
- **After level 3:** Step 5 — Test
- **After level 4:** Step 6 — Pr
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

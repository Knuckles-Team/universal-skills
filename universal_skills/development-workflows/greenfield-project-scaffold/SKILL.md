---
name: greenfield-project-scaffold
description: >-
  Parallel execution workflow for greenfield project scaffold using the Unified Parallel Engine
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
tags: [dev-workflows, greenfield-project-scaffold]
concept: CONCEPT:DEV-001
---

# Greenfield Project Scaffold Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for greenfield project scaffold using the Unified Parallel Engine

## Steps

### Step 1: Spec
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute spec operations for the Greenfield Project Scaffold workflow.
Expected: `spec_artifacts`

### Step 2: Architecture [depends_on: spec]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute architecture operations for the Greenfield Project Scaffold workflow.
Expected: `architecture_artifacts`

### Step 3: Scaffold [depends_on: architecture]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute scaffold operations for the Greenfield Project Scaffold workflow.
Expected: `scaffold_artifacts`

### Step 4: Base Impl [depends_on: scaffold]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute base impl operations for the Greenfield Project Scaffold workflow.
Expected: `base_impl_artifacts`

### Step 5: Ci Setup [depends_on: base_impl]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute ci setup operations for the Greenfield Project Scaffold workflow.
Expected: `ci_setup_artifacts`

### Step 6: Docs [depends_on: ci_setup]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute docs operations for the Greenfield Project Scaffold workflow.
Expected: `docs_artifacts`

### Step 7: KG Persistence [depends_on: docs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Greenfield Project Scaffold results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Spec
- **After level 0:** Step 2 — Architecture
- **After level 1:** Step 3 — Scaffold
- **After level 2:** Step 4 — Base Impl
- **After level 3:** Step 5 — Ci Setup
- **After level 4:** Step 6 — Docs
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

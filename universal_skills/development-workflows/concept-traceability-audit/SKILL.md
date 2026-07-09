---
name: concept-traceability-audit
skill_type: workflow
description: >-
  Parallel execution workflow for concept traceability audit using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: [dev-workflows, concept-traceability-audit]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Concept Traceability Audit Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for concept traceability audit using the Unified Parallel Engine

## Steps

### Step 1: Grep Concept Refs
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute grep concept refs operations for the Concept Traceability Audit workflow.
Expected: `grep_concept_refs_artifacts`

### Step 2: Verify Against Concept Map [depends_on: grep_concept_refs]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute verify against concept map operations for the Concept Traceability Audit workflow.
Expected: `verify_against_concept_map_artifacts`

### Step 3: Report Gaps [depends_on: verify_against_concept_map]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute report gaps operations for the Concept Traceability Audit workflow.
Expected: `report_gaps_artifacts`

### Step 4: KG Persistence [depends_on: report_gaps]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Concept Traceability Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Grep Concept Refs
- **After level 0:** Step 2 — Verify Against Concept Map
- **After level 1:** Step 3 — Report Gaps
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

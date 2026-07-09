---
name: code-walkthrough-library
skill_type: workflow
description: >-
  Parallel execution workflow for code walkthrough library using the Unified Parallel Engine
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
tags: [dev-workflows, code-walkthrough-library]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Code Walkthrough Library Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for code walkthrough library using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Feature Analyze
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per feature analyze operations for the Code Walkthrough Library workflow.
Expected: `fan_out_per_feature_analyze_artifacts`

### Step 2: Interactive Explain [depends_on: fan_out_per_feature_analyze]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute interactive explain operations for the Code Walkthrough Library workflow.
Expected: `interactive_explain_artifacts`

### Step 3: Publish [depends_on: interactive_explain]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute publish operations for the Code Walkthrough Library workflow.
Expected: `publish_artifacts`

### Step 4: KG Persistence [depends_on: publish]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Code Walkthrough Library results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Feature Analyze
- **After level 0:** Step 2 — Interactive Explain
- **After level 1:** Step 3 — Publish
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

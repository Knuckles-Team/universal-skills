---
name: readme-standardization
skill_type: workflow
description: >-
  Parallel execution workflow for readme standardization using the Unified Parallel Engine
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
tags: [dev-workflows, readme-standardization]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# Readme Standardization Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for readme standardization using the Unified Parallel Engine

## Steps

### Step 1: Audit Readme
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute audit readme operations for the Readme Standardization workflow.
Expected: `audit_readme_artifacts`

### Step 2: Update Format [depends_on: audit_readme]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute update format operations for the Readme Standardization workflow.
Expected: `update_format_artifacts`

### Step 3: Add Badges [depends_on: update_format]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute add badges operations for the Readme Standardization workflow.
Expected: `add_badges_artifacts`

### Step 4: Pr [depends_on: add_badges]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Readme Standardization workflow.
Expected: `pr_artifacts`

### Step 5: KG Persistence [depends_on: pr]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Readme Standardization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Audit Readme
- **After level 0:** Step 2 — Update Format
- **After level 1:** Step 3 — Add Badges
- **After level 2:** Step 4 — Pr
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

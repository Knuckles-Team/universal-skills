---
name: overnight-code-improvement
skill_type: workflow
description: >-
  Parallel execution workflow for overnight code improvement using the Unified Parallel Engine
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
tags: [dev-workflows, overnight-code-improvement]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# Overnight Code Improvement Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for overnight code improvement using the Unified Parallel Engine

## Steps

### Step 1: Audit
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute audit operations for the Overnight Code Improvement workflow.
Expected: `audit_artifacts`

### Step 2: Enhance [depends_on: audit]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute enhance operations for the Overnight Code Improvement workflow.
Expected: `enhance_artifacts`

### Step 3: Test [depends_on: enhance]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute test operations for the Overnight Code Improvement workflow.
Expected: `test_artifacts`

### Step 4: Pr [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute pr operations for the Overnight Code Improvement workflow.
Expected: `pr_artifacts`

### Step 5: Report [depends_on: pr]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute report operations for the Overnight Code Improvement workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Overnight Code Improvement results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Audit
- **After level 0:** Step 2 — Enhance
- **After level 1:** Step 3 — Test
- **After level 2:** Step 4 — Pr
- **After level 3:** Step 5 — Report
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

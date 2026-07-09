---
name: test-coverage-campaign
skill_type: workflow
description: >-
  Parallel execution workflow for test coverage campaign using the Unified Parallel Engine
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
tags: [dev-workflows, test-coverage-campaign]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Test Coverage Campaign Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for test coverage campaign using the Unified Parallel Engine

## Steps

### Step 1: Analyze Gaps
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute analyze gaps operations for the Test Coverage Campaign workflow.
Expected: `analyze_gaps_artifacts`

### Step 2: Generate Tests [depends_on: analyze_gaps]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute generate tests operations for the Test Coverage Campaign workflow.
Expected: `generate_tests_artifacts`

### Step 3: Run [depends_on: generate_tests]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute run operations for the Test Coverage Campaign workflow.
Expected: `run_artifacts`

### Step 4: Report [depends_on: run]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute report operations for the Test Coverage Campaign workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Test Coverage Campaign results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Analyze Gaps
- **After level 0:** Step 2 — Generate Tests
- **After level 1:** Step 3 — Run
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

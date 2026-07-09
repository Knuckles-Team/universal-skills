---
name: cross_agent_integration_test
description: >-
  Parallel execution workflow for cross agent integration test using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
tags: [dev-workflows, cross-agent-integration-test]
concept: CONCEPT:DEV-001
---

# Cross Agent Integration Test Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for cross agent integration test using the Unified Parallel Engine

## Steps

### Step 1: Agent A Calls Agent B
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute agent a calls agent b operations for the Cross Agent Integration Test workflow.
Expected: `agent_a_calls_agent_b_artifacts`

### Step 2: Verify E2E [depends_on: agent_a_calls_agent_b]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute verify e2e operations for the Cross Agent Integration Test workflow.
Expected: `verify_e2e_artifacts`

### Step 3: Report [depends_on: verify_e2e]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute report operations for the Cross Agent Integration Test workflow.
Expected: `report_artifacts`

### Step 4: KG Persistence [depends_on: report]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Agent Integration Test results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Agent A Calls Agent B
- **After level 0:** Step 2 — Verify E2E
- **After level 1:** Step 3 — Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

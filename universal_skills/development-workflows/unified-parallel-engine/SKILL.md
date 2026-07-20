---
name: unified-parallel-engine
skill_type: workflow
description: >-
  Parallel execution workflow for agent utilities evolution using the Unified Parallel Engine
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
tags: [dev-workflows, unified-parallel-engine]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# Agent Utilities Evolution Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for agent utilities evolution using the Unified Parallel Engine

## Steps

### Step 1: Scan Papers
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute scan papers operations for the Agent Utilities Evolution workflow.
Expected: `scan_papers_artifacts`

### Step 2: Comparative Analysis [depends_on: scan_papers]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute comparative analysis operations for the Agent Utilities Evolution workflow.
Expected: `comparative_analysis_artifacts`

### Step 3: Sdd Spec [depends_on: comparative_analysis]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute sdd spec operations for the Agent Utilities Evolution workflow.
Expected: `sdd_spec_artifacts`

### Step 4: Implement [depends_on: sdd_spec]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute implement operations for the Agent Utilities Evolution workflow.
Expected: `implement_artifacts`

### Step 5: Test [depends_on: implement]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute test operations for the Agent Utilities Evolution workflow.
Expected: `test_artifacts`

### Step 6: KG Persistence [depends_on: test]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Agent Utilities Evolution results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan Papers
- **After level 0:** Step 2 — Comparative Analysis
- **After level 1:** Step 3 — Sdd Spec
- **After level 2:** Step 4 — Implement
- **After level 3:** Step 5 — Test
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

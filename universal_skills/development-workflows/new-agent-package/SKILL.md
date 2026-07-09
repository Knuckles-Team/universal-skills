---
name: new-agent-package
skill_type: workflow
description: >-
  Parallel execution workflow for new agent package using the Unified Parallel Engine
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
tags: [dev-workflows, new-agent-package]
concept: CONCEPT:DEV-001
metadata:
  version: '1.2.0'
---

# New Agent Package Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for new agent package using the Unified Parallel Engine

## Steps

### Step 1: Scaffold
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute scaffold operations for the New Agent Package workflow.
Expected: `scaffold_artifacts`

### Step 2: Api Client [depends_on: scaffold]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute api client operations for the New Agent Package workflow.
Expected: `api_client_artifacts`

### Step 3: Mcp Server [depends_on: api_client]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute mcp server operations for the New Agent Package workflow.
Expected: `mcp_server_artifacts`

### Step 4: Agent [depends_on: mcp_server]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute agent operations for the New Agent Package workflow.
Expected: `agent_artifacts`

### Step 5: Tests [depends_on: agent]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute tests operations for the New Agent Package workflow.
Expected: `tests_artifacts`

### Step 6: Docs [depends_on: tests]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute docs operations for the New Agent Package workflow.
Expected: `docs_artifacts`

### Step 7: KG Persistence [depends_on: docs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- New Agent Package results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scaffold
- **After level 0:** Step 2 — Api Client
- **After level 1:** Step 3 — Mcp Server
- **After level 2:** Step 4 — Agent
- **After level 3:** Step 5 — Tests
- **After level 4:** Step 6 — Docs
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

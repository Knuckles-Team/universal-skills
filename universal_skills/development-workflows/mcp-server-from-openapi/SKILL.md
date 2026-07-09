---
name: mcp-server-from-openapi
skill_type: workflow
description: >-
  Parallel execution workflow for mcp server from openapi using the Unified Parallel Engine
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
tags: [dev-workflows, mcp-server-from-openapi]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Mcp Server From Openapi Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for mcp server from openapi using the Unified Parallel Engine

## Steps

### Step 1: Fetch Spec
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fetch spec operations for the Mcp Server From Openapi workflow.
Expected: `fetch_spec_artifacts`

### Step 2: Generate Client [depends_on: fetch_spec]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute generate client operations for the Mcp Server From Openapi workflow.
Expected: `generate_client_artifacts`

### Step 3: Build Mcp Tools [depends_on: generate_client]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute build mcp tools operations for the Mcp Server From Openapi workflow.
Expected: `build_mcp_tools_artifacts`

### Step 4: Test [depends_on: build_mcp_tools]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute test operations for the Mcp Server From Openapi workflow.
Expected: `test_artifacts`

### Step 5: Deploy [depends_on: test]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute deploy operations for the Mcp Server From Openapi workflow.
Expected: `deploy_artifacts`

### Step 6: KG Persistence [depends_on: deploy]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Mcp Server From Openapi results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fetch Spec
- **After level 0:** Step 2 — Generate Client
- **After level 1:** Step 3 — Build Mcp Tools
- **After level 2:** Step 4 — Test
- **After level 3:** Step 5 — Deploy
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

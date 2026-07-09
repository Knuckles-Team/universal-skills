---
name: api-documentation-gen
skill_type: workflow
description: >-
  Parallel execution workflow for api documentation gen using the Unified Parallel Engine
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
tags: [dev-workflows, api-documentation-gen]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Api Documentation Gen Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for api documentation gen using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Endpoint Extract Schema
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per endpoint extract schema operations for the Api Documentation Gen workflow.
Expected: `fan_out_per_endpoint_extract_schema_artifacts`

### Step 2: Generate Docs [depends_on: fan_out_per_endpoint_extract_schema]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute generate docs operations for the Api Documentation Gen workflow.
Expected: `generate_docs_artifacts`

### Step 3: Examples [depends_on: generate_docs]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute examples operations for the Api Documentation Gen workflow.
Expected: `examples_artifacts`

### Step 4: Publish [depends_on: examples]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute publish operations for the Api Documentation Gen workflow.
Expected: `publish_artifacts`

### Step 5: KG Persistence [depends_on: publish]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Api Documentation Gen results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Endpoint Extract Schema
- **After level 0:** Step 2 — Generate Docs
- **After level 1:** Step 3 — Examples
- **After level 2:** Step 4 — Publish
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

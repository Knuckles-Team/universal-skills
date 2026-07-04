---
name: config_schema_documentation
description: >-
  Parallel execution workflow for config schema documentation using the Unified Parallel Engine
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
tags: [dev-workflows, config-schema-documentation]
concept: CONCEPT:DEV-001
---

# Config Schema Documentation Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for config schema documentation using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Config Extract Fields
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per config extract fields operations for the Config Schema Documentation workflow.
Expected: `fan_out_per_config_extract_fields_artifacts`

### Step 2: Generate Json Schema [depends_on: fan_out_per_config_extract_fields]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute generate json schema operations for the Config Schema Documentation workflow.
Expected: `generate_json_schema_artifacts`

### Step 3: Publish [depends_on: generate_json_schema]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute publish operations for the Config Schema Documentation workflow.
Expected: `publish_artifacts`

### Step 4: KG Persistence [depends_on: publish]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Config Schema Documentation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Config Extract Fields
- **After level 0:** Step 2 — Generate Json Schema
- **After level 1:** Step 3 — Publish
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

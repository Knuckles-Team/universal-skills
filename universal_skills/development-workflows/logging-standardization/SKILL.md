---
name: logging-standardization
skill_type: workflow
description: >-
  Parallel execution workflow for logging standardization using the Unified Parallel Engine
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
tags: [dev-workflows, logging-standardization]
concept: CONCEPT:DEV-001
metadata:
  version: '1.1.0'
---

# Logging Standardization Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for logging standardization using the Unified Parallel Engine

## Steps

### Step 1: Audit Log Calls
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute audit log calls operations for the Logging Standardization workflow.
Expected: `audit_log_calls_artifacts`

### Step 2: Standardize Format [depends_on: audit_log_calls]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute standardize format operations for the Logging Standardization workflow.
Expected: `standardize_format_artifacts`

### Step 3: Add Structured Logging [depends_on: standardize_format]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute add structured logging operations for the Logging Standardization workflow.
Expected: `add_structured_logging_artifacts`

### Step 4: KG Persistence [depends_on: add_structured_logging]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Logging Standardization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Audit Log Calls
- **After level 0:** Step 2 — Standardize Format
- **After level 1:** Step 3 — Add Structured Logging
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: cross-platform-task-sync
skill_type: workflow
description: >-
  Parallel execution workflow for cross platform task sync using the Unified Parallel Engine
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, cross-platform-task-sync]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.0.2'
---

# Cross Platform Task Sync Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for cross platform task sync using the Unified Parallel Engine

## Steps

### Step 1: Jira
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute jira operations for the Cross Platform Task Sync workflow.
Expected: `jira_artifacts`

### Step 2: Plane
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute plane operations for the Cross Platform Task Sync workflow.
Expected: `plane_artifacts`

### Step 3: Github Issues
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute github issues operations for the Cross Platform Task Sync workflow.
Expected: `github_issues_artifacts`

### Step 4: Unified Dashboard [depends_on: jira, plane, github_issues]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute unified dashboard operations for the Cross Platform Task Sync workflow.
Expected: `unified_dashboard_artifacts`

### Step 5: Sync Status [depends_on: unified_dashboard]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute sync status operations for the Cross Platform Task Sync workflow.
Expected: `sync_status_artifacts`

### Step 6: KG Persistence [depends_on: sync_status]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Platform Task Sync results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Jira; Step 2 — Plane; Step 3 — Github Issues
- **After level 0:** Step 4 — Unified Dashboard
- **After level 1:** Step 5 — Sync Status
- **After level 2:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

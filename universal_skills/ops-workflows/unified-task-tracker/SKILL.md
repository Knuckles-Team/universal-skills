---
name: unified-task-tracker
skill_type: workflow
description: >-
  Automatically discovers and queries configured trackers (Jira/atlassian-agent, Plane/plane-agent, or both) to retrieve assigned and stale issues, present a unified schedule dashboard, and push synced updates.
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
tags: ['atlassian', 'jira', 'plane', 'tasks', 'agile', 'atlassian-agent', 'plane-agent']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.0.2'
---

# Unified Task Tracker Workflow

**CONCEPT:KG-2.12**

Automatically discovers and queries configured trackers (Jira/atlassian-agent, Plane/plane-agent, or both) to retrieve assigned and stale issues, present a unified schedule dashboard, and push synced updates.

## Steps

### Step 0: Atlassian Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Detect configuration and query Jira for issues assigned to currentUser() that are active or stale (updated <= -7d) using atlassian_jira_issue tool.
Expected: `jira_issues`

### Step 1: Plane Agent
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Detect configuration and query Plane for active or stale work items assigned to the user using the plane_work_items tool with list_work_items or search_work_items actions.
Expected: `plane_work_items`

### Step 2: User Interaction
**Agent**: `validator-agent`
**Tools**: `graph_query`

Present a unified dashboard consolidating the active and stale tasks from both Jira and Plane. Prompt the user for progress comments, status updates, or task additions.
Expected: `progress_updates, stale_resolutions`

### Step 3: Atlassian Agent
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Push selected comment updates or status changes back to Jira using the atlassian_jira_comment and atlassian_jira_issue tools.
Expected: `jira_update_results`

### Step 4: Plane Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Push selected comment updates or status changes back to Plane using the plane_work_items tool with create_work_item_comment or update_work_item actions.
Expected: `plane_update_results`

### Step 5: KG Persistence [depends_on: plane-agent]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Unified Task Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Atlassian Agent; Step 1 — Plane Agent; Step 2 — User Interaction; Step 3 — Atlassian Agent; Step 4 — Plane Agent
- **After level 0:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

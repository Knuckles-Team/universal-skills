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
  version: '1.6.2'
---

# Unified Task Tracker Workflow

**CONCEPT:KG-2.12**

Automatically discovers and queries configured trackers (Jira/atlassian-agent, Plane/plane-agent, or both) to retrieve assigned and stale issues, present a unified schedule dashboard, and push synced updates.

## Steps

1. Query Jira with `atlassian_jira_issue` for `assignee = currentUser()` that are active or stale. Verify that `jira_issues` is returned.
2. Query Plane with `plane_list_work_items`. Verify that `plane_work_items` is returned.
3. Present a combined dashboard and collect the user's updates. Verify that `progress_updates` is recorded.
4. Push Jira changes with `atlassian_jira_comment` and `atlassian_jira_issue`. Verify that `jira_update_results` reports success.
5. Push Plane changes with `plane_create_work_item_comment`. Verify that `plane_update_results` reports success.
6. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: Atlassian Issue Discovery [skill: atlassian-agent]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Detect configuration and query Jira for issues assigned to currentUser() that are active or stale (updated <= -7d) using atlassian_jira_issue tool.
Expected: `jira_issues`

### Step 1: Plane Work-Item Discovery [skill: plane-agent]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Detect configuration and query Plane for active or stale work items assigned to the user using `plane_list_work_items` or search_work_items actions.
Expected: `plane_work_items`

### Step 2: User Interaction
**Agent**: `validator-agent`
**Tools**: `graph_query`

Present a unified dashboard consolidating the active and stale tasks from both Jira and Plane. Prompt the user for progress comments, status updates, or task additions.
Expected: `progress_updates, stale_resolutions`

### Step 3: Atlassian Issue Update [skill: atlassian-agent]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Push selected comment updates or status changes back to Jira using the atlassian_jira_comment and atlassian_jira_issue tools.
Expected: `jira_update_results`

### Step 4: Plane Work-Item Update [skill: plane-agent]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Push selected comment updates or status changes back to Plane using `plane_create_work_item_comment` or update_work_item actions.
Expected: `plane_update_results`

### Step 5: KG Persistence [depends_on: Step 4]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Jira query returns 401 | Token expired or wrong URL | Refresh the API token and Jira URL in the agent environment and call `atlassian_jira_issue` again. |
| Plane returns no items | Workspace or project not configured | Set the workspace slug and project id, and call `plane_list_work_items` again. |
| Update fails on a closed issue | Workflow transition not allowed | Look up the allowed transitions and choose a valid status. |

## Output
- Unified Task Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Atlassian Issue Discovery; Step 1 — Plane Work-Item Discovery; Step 2 — User Interaction; Step 3 — Atlassian Issue Update; Step 4 — Plane Work-Item Update
- **After level 0:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

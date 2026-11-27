---
name: atlassian-assigned-issues-manager
skill_type: workflow
description: >-
  Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.
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
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: ['atlassian', 'jira', 'tasks', 'agile', 'atlassian-agent']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.7.0'
---

# Atlassian Assigned Issues Manager Workflow

**CONCEPT:KG-2.12**

Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.

## Steps

1. Query assigned and stale issues with the `atlassian_jira_issue` tool using JQL `assignee = currentUser() AND statusCategory != Done` and `assignee = currentUser() AND updated <= -7d`. Verify that `assigned_issues` and `stale_issues` each contain keys, summaries and updated dates.
2. Present the dashboard of active and stale issues to the user and ask for progress notes. Verify that `progress_inputs` records a user reply for each stale issue or an explicit skip.
3. Draft updates with the `atlassian_jira_comment` tool, or draft new backlog tickets. Verify that `update_results` shows each comment as created or as a draft awaiting approval.
4. Persist the results with `graph_write`. Verify that a `graph_query` for the new nodes returns the issue keys.


### Step 0: Atlassian Assigned-Issue Query [skill: atlassian-agent]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Query Jira for all active tickets assigned to the current user using JQL `assignee = currentUser() AND statusCategory != Done` and stale tickets using `assignee = currentUser() AND updated <= -7d` via atlassian_jira_issue tool.
Expected: `assigned_issues, stale_issues`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Display the active and stale issues dashboard. Prompt the user for notes on recent progress or task updates.
Expected: `progress_inputs, selected_stale_resolutions`

### Step 2: Atlassian Issue-Update Drafting [skill: atlassian-agent]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Create suggested comment updates on Jira issues using atlassian_jira_comment tool, or generate recommended drafts for new backlog tickets to align with current work.
Expected: `update_results, draft_tickets`

### Step 3: KG Persistence [depends_on: Step 2]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| JQL returns no issues | User identity not resolved by the Atlassian server | Run the query with an explicit assignee account id instead of `currentUser()` |
| Comment creation denied | Account lacks comment permission on the project | Save the text as a draft for the user to post and note the permission gap in the report |
| Stale list too large | Many tickets untouched for over 7 days | Group by project and ask the user to pick the top issues before drafting updates |
| `graph_write` fails | Missing typed node metadata | Add the issue key and status fields and repeat the write |

## Output
- Atlassian Assigned Issues Manager results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Atlassian Assigned-Issue Query; Step 1 — User Interaction; Step 2 — Atlassian Issue-Update Drafting
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

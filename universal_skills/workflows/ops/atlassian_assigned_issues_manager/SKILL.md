---
name: atlassian_assigned_issues_manager
description: >-
  Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.
domain: ops
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
---

# Atlassian Assigned Issues Manager Workflow

**CONCEPT:KG-2.12**

Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.

## Steps

### Step 0: Atlassian Agent
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Query Jira for all active tickets assigned to the current user using JQL `assignee = currentUser() AND statusCategory != Done` and stale tickets using `assignee = currentUser() AND updated <= -7d` via atlassian_jira_issue tool.
Expected: `assigned_issues, stale_issues`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Display the active and stale issues dashboard. Prompt the user for notes on recent progress or task updates.
Expected: `progress_inputs, selected_stale_resolutions`

### Step 2: Atlassian Agent
**Agent**: `validator-agent`
**Tools**: `graph_query`

Create suggested comment updates on Jira issues using atlassian_jira_comment tool, or generate recommended drafts for new backlog tickets to align with current work.
Expected: `update_results, draft_tickets`

### Step 3: KG Persistence [depends_on: atlassian-agent]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Atlassian Assigned Issues Manager results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

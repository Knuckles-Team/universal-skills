---
name: atlassian_assigned_issues_manager
description: Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.
domain: ops
tags: ['atlassian', 'jira', 'tasks', 'agile', 'atlassian-agent']
requires: ['atlassian-agent']
---

# atlassian_assigned_issues_manager Workflow

Automatically retrieves issues assigned to the current user, flags tickets older than 7 days, and maps current coding progress to suggest new ticket backlogs.

### Step 0: atlassian-agent
Query Jira for all active tickets assigned to the current user using JQL `assignee = currentUser() AND statusCategory != Done` and stale tickets using `assignee = currentUser() AND updated <= -7d` via atlassian_jira_issue tool.
Expected: assigned_issues, stale_issues

### Step 1: user-interaction
Display the active and stale issues dashboard. Prompt the user for notes on recent progress or task updates.
Expected: progress_inputs, selected_stale_resolutions
Depends On: Step 0

### Step 2: atlassian-agent
Create suggested comment updates on Jira issues using atlassian_jira_comment tool, or generate recommended drafts for new backlog tickets to align with current work.
Expected: update_results, draft_tickets
Depends On: Step 1

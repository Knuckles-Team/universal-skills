---
name: unified_task_tracker
description: Automatically discovers and queries configured trackers (Jira/atlassian-agent, Plane/plane-agent, or both) to retrieve assigned and stale issues, present a unified schedule dashboard, and push synced updates.
domain: ops
tags: ['atlassian', 'jira', 'plane', 'tasks', 'agile', 'atlassian-agent', 'plane-agent']
requires: ['atlassian-agent', 'plane-agent']
---

# unified_task_tracker Workflow

Automatically discovers and queries configured trackers (Jira/atlassian-agent, Plane/plane-agent, or both) to retrieve assigned and stale issues, present a unified schedule dashboard, and push synced updates.

### Step 0: atlassian-agent
Detect configuration and query Jira for issues assigned to currentUser() that are active or stale (updated <= -7d) using atlassian_jira_issue tool.
Expected: jira_issues

### Step 1: plane-agent
Detect configuration and query Plane for active or stale work items assigned to the user using the plane_work_items tool with list_work_items or search_work_items actions.
Expected: plane_work_items

### Step 2: user-interaction
Present a unified dashboard consolidating the active and stale tasks from both Jira and Plane. Prompt the user for progress comments, status updates, or task additions.
Expected: progress_updates, stale_resolutions
Depends On: Step 0, Step 1

### Step 3: atlassian-agent
Push selected comment updates or status changes back to Jira using the atlassian_jira_comment and atlassian_jira_issue tools.
Expected: jira_update_results
Depends On: Step 2

### Step 4: plane-agent
Push selected comment updates or status changes back to Plane using the plane_work_items tool with create_work_item_comment or update_work_item actions.
Expected: plane_update_results
Depends On: Step 2

---
name: cross_platform_task_sync
description: Parallel execution workflow for cross platform task sync using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Cross Platform Task Sync

This workflow defines the topological parallel execution steps for cross platform task sync.

## Steps

### Step 1: jira
Execute the Jira phase for the cross_platform_task_sync workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: jira_artifacts
### Step 2: plane
Execute the Plane phase for the cross_platform_task_sync workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: plane_artifacts
### Step 3: github_issues
Execute the GitHub Issues phase for the cross_platform_task_sync workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: github_issues_artifacts
### Step 4: unified_dashboard [depends_on: jira, plane, github_issues]
Execute the unified dashboard phase for the cross_platform_task_sync workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: unified_dashboard_artifacts
### Step 5: sync_status [depends_on: unified_dashboard]
Execute the sync status phase for the cross_platform_task_sync workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sync_status_artifacts

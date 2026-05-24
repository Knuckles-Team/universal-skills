---
name: sprint_planning_automation
description: Parallel execution workflow for sprint planning automation using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Sprint Planning Automation

This workflow defines the topological parallel execution steps for sprint planning automation.

## Steps

### Step 1: pull_backlog
Execute the pull backlog phase for the sprint_planning_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pull_backlog_artifacts
### Step 2: prioritize [depends_on: pull_backlog]
Execute the prioritize phase for the sprint_planning_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prioritize_artifacts
### Step 3: estimate [depends_on: prioritize]
Execute the estimate phase for the sprint_planning_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: estimate_artifacts
### Step 4: assign [depends_on: estimate]
Execute the assign phase for the sprint_planning_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assign_artifacts
### Step 5: create_sprint [depends_on: assign]
Execute the create sprint phase for the sprint_planning_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: create_sprint_artifacts

---
name: cross_team_dependency_tracker
description: Parallel execution workflow for cross team dependency tracker using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Cross Team Dependency Tracker

This workflow defines the topological parallel execution steps for cross team dependency tracker.

## Steps

### Step 1: scan_blockers
Execute the scan blockers phase for the cross_team_dependency_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_blockers_artifacts
### Step 2: trace_dependencies [depends_on: scan_blockers]
Execute the trace dependencies phase for the cross_team_dependency_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trace_dependencies_artifacts
### Step 3: escalation_report [depends_on: trace_dependencies]
Execute the escalation report phase for the cross_team_dependency_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: escalation_report_artifacts

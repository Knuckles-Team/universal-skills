---
name: capacity_planning_report
description: Parallel execution workflow for capacity planning report using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Capacity Planning Report

This workflow defines the topological parallel execution steps for capacity planning report.

## Steps

### Step 1: velocity
Execute the velocity phase for the capacity_planning_report workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: velocity_artifacts
### Step 2: wip
Execute the WIP phase for the capacity_planning_report workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: wip_artifacts
### Step 3: lead_time
Execute the lead time phase for the capacity_planning_report workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: lead_time_artifacts
### Step 4: forecast [depends_on: velocity, wip, lead_time]
Execute the forecast phase for the capacity_planning_report workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: forecast_artifacts
### Step 5: report [depends_on: forecast]
Execute the report phase for the capacity_planning_report workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts

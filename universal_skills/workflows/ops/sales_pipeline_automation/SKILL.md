---
name: sales_pipeline_automation
description: Parallel execution workflow for sales pipeline automation using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-microsoft
---

# Parallel Workflow: Sales Pipeline Automation

This workflow defines the topological parallel execution steps for sales pipeline automation.

## Steps

### Step 1: qualify_lead
Execute the qualify lead phase for the sales_pipeline_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: qualify_lead_artifacts
### Step 2: demo_scheduling [depends_on: qualify_lead]
Execute the demo scheduling phase for the sales_pipeline_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: demo_scheduling_artifacts
### Step 3: proposal [depends_on: demo_scheduling]
Execute the proposal phase for the sales_pipeline_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: proposal_artifacts
### Step 4: follow_up [depends_on: proposal]
Execute the follow-up phase for the sales_pipeline_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: follow_up_artifacts
### Step 5: close [depends_on: follow_up]
Execute the close phase for the sales_pipeline_automation workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: close_artifacts

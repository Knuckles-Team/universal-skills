---
name: performance_review_cycle
description: Parallel execution workflow for performance review cycle using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-atlassian
---

# Parallel Workflow: Performance Review Cycle

This workflow defines the topological parallel execution steps for performance review cycle.

## Steps

### Step 1: collect_metrics
Execute the collect metrics phase for the performance_review_cycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_metrics_artifacts
### Step 2: peer_feedback [depends_on: collect_metrics]
Execute the peer feedback phase for the performance_review_cycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: peer_feedback_artifacts
### Step 3: draft_review [depends_on: peer_feedback]
Execute the draft review phase for the performance_review_cycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: draft_review_artifacts
### Step 4: schedule [depends_on: draft_review]
Execute the schedule phase for the performance_review_cycle workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_artifacts

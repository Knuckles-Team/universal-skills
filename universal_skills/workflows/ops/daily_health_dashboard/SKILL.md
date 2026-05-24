---
name: daily_health_dashboard
description: Parallel execution workflow for daily health dashboard using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-wger
---

# Parallel Workflow: Daily Health Dashboard

This workflow defines the topological parallel execution steps for daily health dashboard.

## Steps

### Step 1: sleep
Execute the sleep phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: sleep_artifacts
### Step 2: exercise
Execute the exercise phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: exercise_artifacts
### Step 3: nutrition
Execute the nutrition phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: nutrition_artifacts
### Step 4: weight
Execute the weight phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: weight_artifacts
### Step 5: trends [depends_on: sleep, exercise, nutrition, weight]
Execute the trends phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trends_artifacts
### Step 6: recommendations [depends_on: trends]
Execute the recommendations phase for the daily_health_dashboard workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: recommendations_artifacts

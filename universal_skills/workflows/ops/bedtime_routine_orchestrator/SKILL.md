---
name: bedtime_routine_orchestrator
description: Parallel execution workflow for bedtime routine orchestrator using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-home-assistant
---

# Parallel Workflow: Bedtime Routine Orchestrator

This workflow defines the topological parallel execution steps for bedtime routine orchestrator.

## Steps

### Step 1: lights_dim
Execute the lights dim phase for the bedtime_routine_orchestrator workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: lights_dim_artifacts
### Step 2: thermostat_down
Execute the thermostat down phase for the bedtime_routine_orchestrator workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: thermostat_down_artifacts
### Step 3: locks_check
Execute the locks check phase for the bedtime_routine_orchestrator workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: locks_check_artifacts
### Step 4: alarm_set
Execute the alarm set phase for the bedtime_routine_orchestrator workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: alarm_set_artifacts
### Step 5: report [depends_on: lights_dim, thermostat_down, locks_check, alarm_set]
Execute the report phase for the bedtime_routine_orchestrator workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts

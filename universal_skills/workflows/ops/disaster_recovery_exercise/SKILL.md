---
name: disaster_recovery_exercise
description: Parallel execution workflow for disaster recovery exercise using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-ALL infra MCPs
---

# Parallel Workflow: Disaster Recovery Exercise

This workflow defines the topological parallel execution steps for disaster recovery exercise.

## Steps

### Step 1: simulate_failure
Execute the simulate failure phase for the disaster_recovery_exercise workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: simulate_failure_artifacts
### Step 2: parallel_team_response [depends_on: simulate_failure]
Execute the parallel team response phase for the disaster_recovery_exercise workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_team_response_artifacts
### Step 3: validate_recovery [depends_on: parallel_team_response]
Execute the validate recovery phase for the disaster_recovery_exercise workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: validate_recovery_artifacts
### Step 4: debrief [depends_on: validate_recovery]
Execute the debrief phase for the disaster_recovery_exercise workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: debrief_artifacts

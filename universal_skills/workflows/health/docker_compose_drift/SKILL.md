---
name: docker_compose_drift
description: Parallel execution workflow for docker compose drift using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Docker Compose Drift

This workflow defines the topological parallel execution steps for docker compose drift.

## Steps

### Step 1: fan_out_per_stack_get_file
Execute the Fan-out per stack: get file phase for the docker_compose_drift workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_stack_get_file_artifacts
### Step 2: compare_running_state [depends_on: fan_out_per_stack_get_file]
Execute the compare running state phase for the docker_compose_drift workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_running_state_artifacts
### Step 3: drift_report [depends_on: compare_running_state]
Execute the drift report phase for the docker_compose_drift workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: drift_report_artifacts

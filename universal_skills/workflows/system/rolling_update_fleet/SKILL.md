---
name: rolling_update_fleet
description: Parallel execution workflow for rolling update fleet using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-portainer
---

# Parallel Workflow: Rolling Update Fleet

This workflow defines the topological parallel execution steps for rolling update fleet.

## Steps

### Step 1: wave_per_batch_drain
Execute the Wave per batch: drain phase for the rolling_update_fleet workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: wave_per_batch_drain_artifacts
### Step 2: update [depends_on: wave_per_batch_drain]
Execute the update phase for the rolling_update_fleet workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_artifacts
### Step 3: health_check [depends_on: update]
Execute the health check phase for the rolling_update_fleet workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: health_check_artifacts
### Step 4: next_batch [depends_on: health_check]
Execute the next batch phase for the rolling_update_fleet workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: next_batch_artifacts

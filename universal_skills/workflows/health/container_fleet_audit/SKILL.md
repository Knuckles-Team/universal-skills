---
name: container_fleet_audit
description: Parallel execution workflow for container fleet audit using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Container Fleet Audit

This workflow defines the topological parallel execution steps for container fleet audit.

## Steps

### Step 1: fan_out_per_host_list
Execute the Fan-out per host: list phase for the container_fleet_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_list_artifacts
### Step 2: inspect_unhealthy [depends_on: fan_out_per_host_list]
Execute the inspect unhealthy phase for the container_fleet_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: inspect_unhealthy_artifacts
### Step 3: collect_logs [depends_on: inspect_unhealthy]
Execute the collect logs phase for the container_fleet_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_logs_artifacts
### Step 4: remediate [depends_on: collect_logs]
Execute the remediate phase for the container_fleet_audit workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: remediate_artifacts

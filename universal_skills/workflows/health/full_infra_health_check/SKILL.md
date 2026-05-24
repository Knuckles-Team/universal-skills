---
name: full_infra_health_check
description: Parallel execution workflow for full infra health check using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-all infra MCPs
---

# Parallel Workflow: Full Infra Health Check

This workflow defines the topological parallel execution steps for full infra health check.

## Steps

### Step 1: containers
Execute the containers phase for the full_infra_health_check workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: containers_artifacts
### Step 2: dns
Execute the DNS phase for the full_infra_health_check workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dns_artifacts
### Step 3: uptime
Execute the uptime phase for the full_infra_health_check workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: uptime_artifacts
### Step 4: disks
Execute the disks phase for the full_infra_health_check workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: disks_artifacts
### Step 5: memory
Execute the memory phase for the full_infra_health_check workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: memory_artifacts

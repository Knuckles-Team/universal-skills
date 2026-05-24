---
name: container_resource_limits
description: Parallel execution workflow for container resource limits using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-container-manager
---

# Parallel Workflow: Container Resource Limits

This workflow defines the topological parallel execution steps for container resource limits.

## Steps

### Step 1: inspect_all
Execute the inspect all phase for the container_resource_limits workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: inspect_all_artifacts
### Step 2: identify_unlimited [depends_on: inspect_all]
Execute the identify unlimited phase for the container_resource_limits workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_unlimited_artifacts
### Step 3: apply_policies [depends_on: identify_unlimited]
Execute the apply policies phase for the container_resource_limits workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: apply_policies_artifacts
### Step 4: verify [depends_on: apply_policies]
Execute the verify phase for the container_resource_limits workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts

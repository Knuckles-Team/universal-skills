---
name: network_segmentation
description: Parallel execution workflow for network segmentation using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Network Segmentation

This workflow defines the topological parallel execution steps for network segmentation.

## Steps

### Step 1: audit_current
Execute the audit current phase for the network_segmentation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: audit_current_artifacts
### Step 2: design_vlans [depends_on: audit_current]
Execute the design VLANs phase for the network_segmentation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: design_vlans_artifacts
### Step 3: implement [depends_on: design_vlans]
Execute the implement phase for the network_segmentation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: implement_artifacts
### Step 4: verify_isolation [depends_on: implement]
Execute the verify isolation phase for the network_segmentation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_isolation_artifacts

---
name: host_hardware_inventory
description: Parallel execution workflow for host hardware inventory using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-systems-manager
---

# Parallel Workflow: Host Hardware Inventory

This workflow defines the topological parallel execution steps for host hardware inventory.

## Steps

### Step 1: fan_out_per_host_cpu
Execute the Fan-out per host: CPU phase for the host_hardware_inventory workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_cpu_artifacts
### Step 2: gpu
Execute the GPU phase for the host_hardware_inventory workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gpu_artifacts
### Step 3: ram
Execute the RAM phase for the host_hardware_inventory workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ram_artifacts
### Step 4: disk
Execute the disk phase for the host_hardware_inventory workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: disk_artifacts
### Step 5: kg_ingest [depends_on: fan_out_per_host_cpu, gpu, ram, disk]
Execute the KG ingest phase for the host_hardware_inventory workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_ingest_artifacts

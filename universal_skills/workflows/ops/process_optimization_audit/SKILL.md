---
name: process_optimization_audit
description: Parallel execution workflow for process optimization audit using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Process Optimization Audit

This workflow defines the topological parallel execution steps for process optimization audit.

## Steps

### Step 1: fan_out_per_process_map_current
Execute the Fan-out per process: map current phase for the process_optimization_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_process_map_current_artifacts
### Step 2: identify_waste [depends_on: fan_out_per_process_map_current]
Execute the identify waste phase for the process_optimization_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_waste_artifacts
### Step 3: propose_improvements [depends_on: identify_waste]
Execute the propose improvements phase for the process_optimization_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: propose_improvements_artifacts
### Step 4: roi [depends_on: propose_improvements]
Execute the ROI phase for the process_optimization_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: roi_artifacts

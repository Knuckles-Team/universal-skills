---
name: multi_host_command_exec
description: Parallel execution workflow for multi host command exec using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Multi Host Command Exec

This workflow defines the topological parallel execution steps for multi host command exec.

## Steps

### Step 1: fan_out_per_host_ssh_execute
Execute the Fan-out per host: SSH execute phase for the multi_host_command_exec workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_host_ssh_execute_artifacts
### Step 2: collect_output [depends_on: fan_out_per_host_ssh_execute]
Execute the collect output phase for the multi_host_command_exec workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_output_artifacts
### Step 3: aggregate [depends_on: collect_output]
Execute the aggregate phase for the multi_host_command_exec workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: aggregate_artifacts

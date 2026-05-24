---
name: ssh_key_rotation
description: Parallel execution workflow for ssh key rotation using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-tunnel-manager
---

# Parallel Workflow: Ssh Key Rotation

This workflow defines the topological parallel execution steps for ssh key rotation.

## Steps

### Step 1: generate_new_keys
Execute the generate new keys phase for the ssh_key_rotation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_new_keys_artifacts
### Step 2: distribute [depends_on: generate_new_keys]
Execute the distribute phase for the ssh_key_rotation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: distribute_artifacts
### Step 3: update_configs [depends_on: distribute]
Execute the update configs phase for the ssh_key_rotation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_configs_artifacts
### Step 4: revoke_old [depends_on: update_configs]
Execute the revoke old phase for the ssh_key_rotation workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: revoke_old_artifacts

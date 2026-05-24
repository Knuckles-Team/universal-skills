---
name: ansible_playbook_runner
description: Parallel execution workflow for ansible playbook runner using the Unified Parallel Engine
domain: infra
tags:
  - parallel-workflow
  - infra
  - mcp-ansible-tower
---

# Parallel Workflow: Ansible Playbook Runner

This workflow defines the topological parallel execution steps for ansible playbook runner.

## Steps

### Step 1: inventory_scan
Execute the inventory scan phase for the ansible_playbook_runner workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: inventory_scan_artifacts
### Step 2: playbook_select [depends_on: inventory_scan]
Execute the playbook select phase for the ansible_playbook_runner workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: playbook_select_artifacts
### Step 3: execute [depends_on: playbook_select]
Execute the execute phase for the ansible_playbook_runner workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: execute_artifacts
### Step 4: verify [depends_on: execute]
Execute the verify phase for the ansible_playbook_runner workflow under the infra domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_artifacts

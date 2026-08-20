---
name: host-hardware-inventory
skill_type: workflow
description: >-
  Collect hardware profile details (CPU, memory, disk, OS, GPU/accelerator) and
  current resource utilization across reachable hardware nodes. Use when a fleet
  operator needs a consolidated hardware and current-utilization inventory; this
  workflow is read-only.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: host-hardware-inventory-team
  task_pattern: fleet hardware profile and utilization inventory
  execution_mode: sequential
  specialist_ids:
    - hardware-profile-sweep
    - host-resource-sampler
tags: [health, infrastructure, hardware, inventory]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Host Hardware Inventory Workflow

Compose the named atomic skills without adding new discovery logic here.

## Inputs

Provide the target hardware node selection.

## Steps

### Step 0: hardware-profile-sweep [skill: hardware-profile-sweep]

Invoke `$hardware-profile-sweep` with the workflow inputs to collect
CPU, memory, disk, OS, and GPU/accelerator details across the nodes.

Expected: `hardware_profile`

### Step 1: host-resource-sampler [skill: host-resource-sampler] [depends_on: Step 0]

Invoke `$host-resource-sampler` with `hardware_profile`'s node
selection to sample current utilization for the same nodes.

Expected: `resource_sample`

## Output

Return `hardware_profile` and `resource_sample` as the consolidated inventory.

## Execution

- **Run first:** Step 0 — `$hardware-profile-sweep`.
- **After level 0:** Step 1 — `$host-resource-sampler`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

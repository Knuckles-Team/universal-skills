---
name: disk-space-remediation
skill_type: workflow
description: >-
  Sample a host's current resource utilization and then discover and safely
  reclaim disk space where it is under pressure. Use when a filesystem is full
  or nearly full and a host needs a governed reclamation pass; this workflow
  never deletes anything outside the reclaimer's own safety checks.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: disk-space-remediation-team
  task_pattern: host disk-pressure sampling and safe reclamation
  execution_mode: sequential
  specialist_ids:
    - host-resource-sampler
    - host-disk-reclaimer
tags: [health, infrastructure, disk]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.3.1'
  author: Genius
---

# Disk Space Remediation Workflow

Compose the named atomic skills without adding new deletion logic here.

## Inputs

Provide the target host(s) and the reclamation risk tolerance.

## Steps

### Step 0: host-resource-sampler [skill: host-resource-sampler]

Invoke `$host-resource-sampler` with the workflow inputs to sample
current CPU, memory, disk, and load metrics.

Expected: `resource_sample`

### Step 1: host-disk-reclaimer [skill: host-disk-reclaimer] [depends_on: Step 0]

Invoke `$host-disk-reclaimer` with `resource_sample` to discover disk
consumers and safely reclaim space.

Expected: `reclamation_report`

## Output

Return `resource_sample` and `reclamation_report`.

## Execution

- **Run first:** Step 0 — `$host-resource-sampler`.
- **After level 0:** Step 1 — `$host-disk-reclaimer`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

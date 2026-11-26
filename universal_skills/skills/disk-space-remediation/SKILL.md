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
  version: '1.6.2'
  author: Knuckles-Team
---

# Disk Space Remediation Workflow

Compose the named atomic skills without adding new deletion logic here.

## Inputs

Provide the target host(s) and the reclamation risk tolerance.

## Steps

1. Sample the target host with `$host-resource-sampler` using the workflow inputs. Verify that the `resource_sample` output lists CPU, memory, disk and load values for every target host.
2. Reclaim space with `$host-disk-reclaimer` by passing `resource_sample` into it. Verify that the returned `reclamation_report` names each path it reclaimed and that every action stayed inside the reclaimer's own safety checks.

### Step 0: host-resource-sampler [skill: host-resource-sampler]

Invoke `$host-resource-sampler` with the workflow inputs to sample
current CPU, memory, disk, and load metrics.

Expected: `resource_sample`

### Step 1: host-disk-reclaimer [skill: host-disk-reclaimer] [depends_on: Step 0]

Invoke `$host-disk-reclaimer` with `resource_sample` to discover disk
consumers and safely reclaim space.

Expected: `reclamation_report`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `resource_sample` is empty for a host | Host unreachable or sampler lacks access | Confirm connectivity with `ssh <host> true` and re-invoke `$host-resource-sampler` against the reachable hosts only. |
| `reclamation_report` shows nothing reclaimed | No filesystem crossed the pressure threshold or the risk tolerance was too strict | Inspect the disk figures in `resource_sample` and raise the stated risk tolerance input before re-invoking `$host-disk-reclaimer`. |
| A deletion was proposed outside the reclaimer's safety checks | Step logic was extended in this workflow | Remove the extra deletion logic and let `$host-disk-reclaimer` own all deletes. |

## Output

Return `resource_sample` and `reclamation_report`.

## Execution

- **Run first:** Step 0 — `$host-resource-sampler`.
- **After level 0:** Step 1 — `$host-disk-reclaimer`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

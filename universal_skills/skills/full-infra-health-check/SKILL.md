---
name: full-infra-health-check
skill_type: workflow
description: >-
  Run every health-relevant atomic skill this catalog owns — hardware profile,
  current resource utilization, compose configuration drift, and TLS expiry —
  in parallel across the fleet, then consolidate the findings into one formatted
  report. Use when an operator wants a single point-in-time snapshot combining
  every owned infrastructure health signal; this workflow is read-only.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: full-infra-health-check-team
  task_pattern: consolidated multi-signal fleet health snapshot
  execution_mode: parallel
  specialist_ids:
    - hardware-profile-sweep
    - host-resource-sampler
    - docker-compose-drift-detector
    - ssl-expiry-checker
    - document-converter
tags: [health, infrastructure, monitoring]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Full Infrastructure Health Check Workflow

Compose the named atomic skills without adding new health-scoring logic here.

## Inputs

Provide the fleet's host/stack/endpoint selection and the git configuration
reference.

## Steps

1. Collect hardware details by invoking `$hardware-profile-sweep`. Verify that `hardware_profile` has an entry for each host.
2. Sample utilization by invoking `$host-resource-sampler`. Verify that `resource_sample` includes CPU, memory and disk values.
3. Detect drift by invoking `$docker-compose-drift-detector`. Verify that `drift_report` includes `drift_detected`.
4. Check certificates by invoking `$ssl-expiry-checker`. Verify that `expiry_report` lists the expiry date of each endpoint.
5. Render the report by invoking `$document-converter` with all four outputs. Verify that `health_check_document` opens and contains all four sections.

### Step 0: hardware-profile-sweep [skill: hardware-profile-sweep]

Invoke `$hardware-profile-sweep` with the workflow inputs to collect
hardware details across the fleet.

Expected: `hardware_profile`

### Step 1: host-resource-sampler [skill: host-resource-sampler]

Invoke `$host-resource-sampler` with the workflow inputs to sample
current utilization across the fleet.

Expected: `resource_sample`

### Step 2: docker-compose-drift-detector [skill: docker-compose-drift-detector]

Invoke `$docker-compose-drift-detector` with the workflow inputs to
compare running compose state against git configuration.

Expected: `drift_report`

### Step 3: ssl-expiry-checker [skill: ssl-expiry-checker]

Invoke `$ssl-expiry-checker` with the workflow inputs to check TLS
certificate expiry across the fleet's endpoints.

Expected: `expiry_report`

### Step 4: document-converter [skill: document-converter] [depends_on: Step 0, Step 1, Step 2, Step 3]

Invoke `$document-converter` with `hardware_profile`,
`resource_sample`, `drift_report`, and `expiry_report` to render one consolidated
Markdown/PDF health-check report.

Expected: `health_check_document`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A host missing from the profile | Host unreachable | Check connectivity with `ssh <host> true` and rerun that sweep. |
| `expiry_report` empty | Endpoint list not supplied | Add endpoints to the inputs and re-invoke `$ssl-expiry-checker`. |
| Report lacks a section | One upstream output was empty | Rerun the missing step and regenerate with `$document-converter`. |

## Output

Return `hardware_profile`, `resource_sample`, `drift_report`, `expiry_report`,
and `health_check_document`.

## Execution

- **Run first (in parallel):** Step 0 — `$hardware-profile-sweep`, Step 1 — `$host-resource-sampler`, Step 2 — `$docker-compose-drift-detector`, Step 3 — `$ssl-expiry-checker`.
- **After level 0:** Step 4 — `$document-converter`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

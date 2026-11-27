---
name: container-fleet-audit
skill_type: workflow
description: >-
  Detect drift between the fleet's running Docker Compose/Swarm state and its
  git configuration across all registered stacks, then render the findings as a
  formatted audit report. Use when a fleet operator needs a point-in-time
  fleet-wide drift audit; this workflow is read-only and does not redeploy.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: container-fleet-audit-team
  task_pattern: fleet-wide compose drift audit and report
  execution_mode: sequential
  specialist_ids:
    - docker-compose-drift-detector
    - document-converter
tags: [health, infrastructure, docker, fleet, audit]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Container Fleet Audit Workflow

Compose the named atomic skills without adding new comparison logic here.

## Inputs

Provide the fleet's stack selection and the git configuration reference.

## Steps

1. Collect the stack selection and the git configuration reference from the caller. Verify that `ls` on the git configuration path shows a compose file for every selected stack.
2. Compare each stack's running state against git with `docker-compose-drift-detector` (Step 0). Verify that `drift_report` has one entry per selected stack, each marked in-sync or drifted.
3. Render the report with `document-converter` from `drift_report` (Step 1). Verify that `audit_document` opens as Markdown or PDF and lists the same stacks as `drift_report`.

### Step 0: docker-compose-drift-detector [skill: docker-compose-drift-detector]

Invoke `$docker-compose-drift-detector` with the workflow inputs to
compare each stack's running state against git configuration.

Expected: `drift_report`

### Step 1: document-converter [skill: document-converter] [depends_on: Step 0]

Invoke `$document-converter` with `drift_report` to render it as a
formatted Markdown/PDF fleet audit report.

Expected: `audit_document`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `drift_report` omits a stack | The stack name does not match the compose project name | Run `docker compose ls` to list the real project names and pass them to Step 0 |
| Every stack shows as drifted | The git reference points at the wrong branch or path | Check the git reference with `git -C <path> branch --show-current` and point Step 0 at the intended branch |
| `audit_document` is empty | `document-converter` received an empty `drift_report` | Rerun Step 0 first, confirm `drift_report` is non-empty, and pass it to Step 1 again |


## Output

Return `drift_report` and `audit_document`. Read-only; does not redeploy.

## Execution

- **Run first:** Step 0 — `$docker-compose-drift-detector`.
- **After level 0:** Step 1 — `$document-converter`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

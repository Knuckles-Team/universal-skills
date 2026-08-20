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
  version: '1.3.0'
  author: Genius
---

# Container Fleet Audit Workflow

Compose the named atomic skills without adding new comparison logic here.

## Inputs

Provide the fleet's stack selection and the git configuration reference.

## Steps

### Step 0: docker-compose-drift-detector [skill: docker-compose-drift-detector]

Invoke `$docker-compose-drift-detector` with the workflow inputs to
compare each stack's running state against git configuration.

Expected: `drift_report`

### Step 1: document-converter [skill: document-converter] [depends_on: Step 0]

Invoke `$document-converter` with `drift_report` to render it as a
formatted Markdown/PDF fleet audit report.

Expected: `audit_document`

## Output

Return `drift_report` and `audit_document`. Read-only; does not redeploy.

## Execution

- **Run first:** Step 0 — `$docker-compose-drift-detector`.
- **After level 0:** Step 1 — `$document-converter`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

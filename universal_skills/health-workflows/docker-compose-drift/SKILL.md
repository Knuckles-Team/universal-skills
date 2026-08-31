---
name: docker-compose-drift
skill_type: workflow
description: >-
  Detect drift between a host's running Docker Compose/Swarm state and its git
  configuration, then compile and redeploy the declared configuration where the
  operator confirms remediation. Use when a stack's live state may have diverged
  from its source of truth; this workflow never redeploys without the drift
  report as evidence.
domain: health-workflows
license: MIT
requires: []
agent: infra-health-orchestrator
team_config:
  name: docker-compose-drift-team
  task_pattern: compose drift detection and confirmed remediation
  execution_mode: sequential
  specialist_ids:
    - docker-compose-drift-detector
    - docker-compose-operator
tags: [health, infrastructure, docker, drift]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.3.1'
  author: Genius
---

# Docker Compose Drift Workflow

Compose the named atomic skills without adding new comparison logic here.

## Inputs

Provide the target host(s)/stack(s) and the git configuration reference.

## Steps

### Step 0: docker-compose-drift-detector [skill: docker-compose-drift-detector]

Invoke `$docker-compose-drift-detector` with the workflow inputs to
compare running state against git configuration.

Expected: `drift_report`

### Step 1: docker-compose-operator [skill: docker-compose-operator] [depends_on: Step 0]

Invoke `$docker-compose-operator` with `drift_report` to compile and
redeploy the declared configuration for confirmed drift.

Expected: `remediation_result`

## Output

Return `drift_report` and `remediation_result`.

## Execution

- **Run first:** Step 0 — `$docker-compose-drift-detector`.
- **After level 0:** Step 1 — `$docker-compose-operator`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

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
  version: '1.6.2'
  author: Knuckles-Team
---

# Docker Compose Drift Workflow

Compose the named atomic skills without adding new comparison logic here.

## Inputs

Provide the target host(s)/stack(s) and the git configuration reference.

## Steps

1. Detect drift by invoking `$docker-compose-drift-detector` with the target stacks and git reference. Verify that `drift_report` contains `drift_detected` and a `severity` value.
2. Remediate confirmed drift by invoking `$docker-compose-operator` with `drift_report` after operator confirmation. Verify that `remediation_result` reports `status` SUCCESS and that rerunning `$docker-compose-drift-detector` shows `drift_detected` false.

### Step 0: docker-compose-drift-detector [skill: docker-compose-drift-detector]

Invoke `$docker-compose-drift-detector` with the workflow inputs to
compare running state against git configuration.

Expected: `drift_report`

### Step 1: docker-compose-operator [skill: docker-compose-operator] [depends_on: Step 0]

Invoke `$docker-compose-operator` with `drift_report` to compile and
redeploy the declared configuration for confirmed drift.

Expected: `remediation_result`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `drift_report` cannot be produced | `container-manager-mcp` is unreachable or the git reference is wrong | Check the container-manager connection and the git reference input, and re-invoke `$docker-compose-drift-detector` with the corrected values. |
| Remediation attempted without a drift report | Step order was skipped | Stop and run `$docker-compose-drift-detector` first, because redeploy requires the report as evidence. |
| `remediation_result` reports FAILED | Compose manifest invalid or a dependency was down | Read `health_log_summary` from `$docker-compose-operator`, fix the manifest or the dependency and redeploy that stack only. |

## Output

Return `drift_report` and `remediation_result`.

## Execution

- **Run first:** Step 0 — `$docker-compose-drift-detector`.
- **After level 0:** Step 1 — `$docker-compose-operator`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

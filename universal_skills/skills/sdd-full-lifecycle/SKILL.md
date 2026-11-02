---
name: sdd-full-lifecycle
domain: development-workflows
skill_type: workflow
description: >-
  Compose intake, tracked Spec Kit specification, task planning, verification,
  implementation, and testing for an approved change with a supplied design plan.
license: MIT
requires: []
agent: sdd-lifecycle-orchestrator
team_config:
  name: sdd-full-lifecycle-team
  task_pattern: spec-driven development from intake through automated verification
  execution_mode: sequential
  specialist_ids:
    - speckit-specify
    - speckit-plan
    - speckit-tasks
    - speckit-analyze
    - sdd-implementer
    - automated-test-runner
tags: [sdd, specification, planning, implementation, testing]
concept: CONCEPT:DEV-001
metadata:
  version: '1.5.2'
  author: Genius
---

# SDD Full Lifecycle Workflow

## Steps

### Step 0: speckit-specify [skill: speckit-specify]

Invoke `$speckit-specify` with the workflow request.

Expected: `specification`

### Step 1: speckit-plan [skill: speckit-plan] [depends_on: Step 0]

Invoke `$speckit-plan` with `specification` and the supplied design plan.

Expected: `plan`

### Step 2: speckit-tasks [skill: speckit-tasks] [depends_on: Step 1]

Invoke `$speckit-tasks` with `specification`, `plan.md` and the design artifacts.

Expected: `tasks`

### Step 3: speckit-analyze [skill: speckit-analyze] [depends_on: Step 2]

Invoke `$speckit-analyze` with `specification`, `plan.md` and `tasks`.

Expected: `verified_specification`

### Step 4: sdd-implementer [skill: sdd-implementer] [depends_on: Step 3]

Invoke `$sdd-implementer` with `verified_specification` and `tasks`.

Expected: `implementation_result`

### Step 5: automated-test-runner [skill: automated-test-runner] [depends_on: Step 4]

Invoke `$automated-test-runner` with `implementation_result`.

Expected: `test_result`

## Execution

The workflow input must include a tracked `specs/<stable-id>/plan.md` and applicable design artifacts produced with the repository’s Spec Kit plan command. The current DAG has no atomic plan-generation skill; it must stop before task planning if the design is absent. `.specify/memory/constitution.md` governs each step. Git-tracked `specs/` files are authoritative; KG sync is derived.

- **Run first:** Step 0 — `$speckit-specify`.
- **After Step 0:** Step 1 — `$speckit-plan`.
- **After Step 1:** Step 2 — `$speckit-tasks`.
- **After Step 2:** Step 3 — `$speckit-analyze`.
- **After Step 3:** Step 4 — `$sdd-implementer`.
- **After Step 4:** Step 5 — `$automated-test-runner`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

## Delivery practice

Follow the [delivery practice reference](https://github.com/Knuckles-Team/pipelines/blob/main/reference/delivery-practice.md) for waiting, branches, merge holds, worktree safety and verification. The [constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) holds the binding articles: XXVIII (merges and releases), XXIX (checks tell the truth), XVIII (landed means reachable) and XXV (small units).

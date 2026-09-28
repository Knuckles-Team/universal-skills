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
    - spec-intake-wizard
    - spec-generator
    - task-planner
    - spec-verifier
    - sdd-implementer
    - automated-test-runner
tags: [sdd, specification, planning, implementation, testing]
concept: CONCEPT:DEV-001
metadata:
  version: '1.3.1'
  author: Genius
---

# SDD Full Lifecycle Workflow

## Steps

### Step 0: spec-intake-wizard [skill: spec-intake-wizard]

Invoke `$spec-intake-wizard` with the workflow request.

Expected: `intake_result`

### Step 1: spec-generator [skill: spec-generator] [depends_on: Step 0]

Invoke `$spec-generator` with `intake_result`.

Expected: `specification`

### Step 2: task-planner [skill: task-planner] [depends_on: Step 1]

Invoke `$task-planner` with `specification` and the supplied `specs/<stable-id>/plan.md` and design artifacts.

Expected: `tasks`

### Step 3: spec-verifier [skill: spec-verifier] [depends_on: Step 2]

Invoke `$spec-verifier` with `specification`, `plan.md`, and `tasks`.

Expected: `verified_specification`

### Step 4: sdd-implementer [skill: sdd-implementer] [depends_on: Step 3]

Invoke `$sdd-implementer` with `verified_specification` and `tasks`.

Expected: `implementation_result`

### Step 5: automated-test-runner [skill: automated-test-runner] [depends_on: Step 4]

Invoke `$automated-test-runner` with `implementation_result`.

Expected: `test_result`

## Execution

The workflow input must include a tracked `specs/<stable-id>/plan.md` and applicable design artifacts produced with the repository’s Spec Kit plan command. The current DAG has no atomic plan-generation skill; it must stop before task planning if the design is absent. `.specify/memory/constitution.md` governs each step. Git-tracked `specs/` files are authoritative; KG sync is derived.

- **Run first:** Step 0 — `$spec-intake-wizard`.
- **After Step 0:** Step 1 — `$spec-generator`.
- **After Step 1:** Step 2 — `$task-planner`.
- **After Step 2:** Step 3 — `$spec-verifier`.
- **After Step 3:** Step 4 — `$sdd-implementer`.
- **After Step 4:** Step 5 — `$automated-test-runner`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: sdd-full-lifecycle
description: >-
  End-to-end Spec-Driven Development: requirements parsing, concurrent implementation, QA test generation, and walkthrough verification.
domain: dev-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
    - validator-agent
    - publisher-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
    publisher-agent: [rep_rm_git, gl_merge_requests]
tags: [sdd, backend, frontend, qa, devops, verification]
concept: CONCEPT:DEV-001
---

# Sdd Full Lifecycle Workflow

**CONCEPT:DEV-001**

End-to-end Spec-Driven Development: requirements parsing, concurrent implementation, QA test generation, and walkthrough verification.

## Steps

### Step 1: Spec Generator
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Create robust functional specifications, user story maps, and detailed acceptance criteria from raw requirements.
Expected: `design-spec-produced`

### Step 2: Python Backend Engineer [depends_on: spec-generator]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Implement stable database schemas, REST or gRPC controller endpoints, and business service validations matching the specification.
Expected: `backend-built`

### Step 3: Typescript Frontend Developer [depends_on: spec-generator]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Develop modern, beautiful reactive UI page layouts, state managers, and network fetch hooks based on the specification.
Expected: `frontend-built`

### Step 4: Qa Test Engineer [depends_on: spec-generator]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Write extensive pytest unit suites, backend endpoint test modules, and frontend integration or end-to-end browser tests.
Expected: `tests-written`

### Step 5: Verification Gate [depends_on: python-backend-engineer, typescript-frontend-developer, qa-test-engineer]
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute the test suites, perform code coverage checks, run security audits, and generate a final walkthrough presentation.
Expected: `product-verified`

### Step 6: KG Persistence [depends_on: Verification Gate]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Sdd Full Lifecycle results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Spec Generator
- **After level 0:** Step 2 — Python Backend Engineer; Step 3 — Typescript Frontend Developer; Step 4 — Qa Test Engineer
- **After level 1:** Step 5 — Verification Gate
- **After level 2:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

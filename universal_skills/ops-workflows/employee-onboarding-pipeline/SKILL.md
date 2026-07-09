---
name: employee-onboarding-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for employee onboarding pipeline using the Unified Parallel Engine
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, employee-onboarding-pipeline]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.1.0'
---

# Employee Onboarding Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for employee onboarding pipeline using the Unified Parallel Engine

## Steps

### Step 1: Create Accounts
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute create accounts operations for the Employee Onboarding Pipeline workflow.
Expected: `create_accounts_artifacts`

### Step 2: Setup Access [depends_on: create_accounts]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute setup access operations for the Employee Onboarding Pipeline workflow.
Expected: `setup_access_artifacts`

### Step 3: Assign Equipment [depends_on: setup_access]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute assign equipment operations for the Employee Onboarding Pipeline workflow.
Expected: `assign_equipment_artifacts`

### Step 4: Training Schedule [depends_on: assign_equipment]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute training schedule operations for the Employee Onboarding Pipeline workflow.
Expected: `training_schedule_artifacts`

### Step 5: Checklist [depends_on: training_schedule]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute checklist operations for the Employee Onboarding Pipeline workflow.
Expected: `checklist_artifacts`

### Step 6: KG Persistence [depends_on: checklist]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Employee Onboarding Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Create Accounts
- **After level 0:** Step 2 — Setup Access
- **After level 1:** Step 3 — Assign Equipment
- **After level 2:** Step 4 — Training Schedule
- **After level 3:** Step 5 — Checklist
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

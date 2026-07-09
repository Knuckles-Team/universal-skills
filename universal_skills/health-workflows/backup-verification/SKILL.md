---
name: backup-verification
skill_type: workflow
description: >-
  Parallel execution workflow for backup verification using the Unified Parallel Engine
domain: health-workflows
agent: health_wellness_coordinator
team_config:
  name: health_wellness_team
  task_pattern: health monitoring and wellness optimization
  execution_mode: sequential
  specialist_ids:
    - data-collector
    - analyzer-agent
    - planner-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
tags: [health, backup-verification]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.0.2'
---

# Backup Verification Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for backup verification using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Backup Target Restore Test
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per backup target restore test operations for the Backup Verification workflow.
Expected: `fan_out_per_backup_target_restore_test_artifacts`

### Step 2: Integrity Check [depends_on: fan_out_per_backup_target_restore_test]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute integrity check operations for the Backup Verification workflow.
Expected: `integrity_check_artifacts`

### Step 3: Report [depends_on: integrity_check]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute report operations for the Backup Verification workflow.
Expected: `report_artifacts`

### Step 4: KG Persistence [depends_on: report]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Backup Verification results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Backup Target Restore Test
- **After level 0:** Step 2 — Integrity Check
- **After level 1:** Step 3 — Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

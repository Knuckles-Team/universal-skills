---
name: backup_verification
description: >-
  Parallel execution workflow for backup verification using the Unified Parallel Engine
domain: health
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

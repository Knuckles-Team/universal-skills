---
name: disk_space_remediation
description: >-
  Parallel execution workflow for disk space remediation using the Unified Parallel Engine
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
    - tracker-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
    tracker-agent: [nc_calendar, graph_write]
tags: [health, disk-space-remediation]
concept: CONCEPT:HEALTH-001
---

# Disk Space Remediation Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for disk space remediation using the Unified Parallel Engine

## Steps

### Step 1: Sequential Scan
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute sequential scan operations for the Disk Space Remediation workflow.
Expected: `sequential_scan_artifacts`

### Step 2: Identify Bloat [depends_on: sequential_scan]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute identify bloat operations for the Disk Space Remediation workflow.
Expected: `identify_bloat_artifacts`

### Step 3: Prune [depends_on: identify_bloat]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute prune operations for the Disk Space Remediation workflow.
Expected: `prune_artifacts`

### Step 4: Verify [depends_on: prune]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute verify operations for the Disk Space Remediation workflow.
Expected: `verify_artifacts`

### Step 5: KG Persistence [depends_on: verify]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Disk Space Remediation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

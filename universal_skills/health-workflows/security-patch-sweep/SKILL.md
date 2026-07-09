---
name: security-patch-sweep
skill_type: workflow
description: >-
  Parallel execution workflow for security patch sweep using the Unified Parallel Engine
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
    - tracker-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
    tracker-agent: [nc_calendar, graph_write]
tags: [health, security-patch-sweep]
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.2.0'
---

# Security Patch Sweep Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for security patch sweep using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host Check Updates
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per host check updates operations for the Security Patch Sweep workflow.
Expected: `fan_out_per_host_check_updates_artifacts`

### Step 2: Cve Scan [depends_on: fan_out_per_host_check_updates]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute cve scan operations for the Security Patch Sweep workflow.
Expected: `cve_scan_artifacts`

### Step 3: Apply Patches [depends_on: cve_scan]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute apply patches operations for the Security Patch Sweep workflow.
Expected: `apply_patches_artifacts`

### Step 4: Reboot Schedule [depends_on: apply_patches]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute reboot schedule operations for the Security Patch Sweep workflow.
Expected: `reboot_schedule_artifacts`

### Step 5: KG Persistence [depends_on: reboot_schedule]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Security Patch Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Host Check Updates
- **After level 0:** Step 2 — Cve Scan
- **After level 1:** Step 3 — Apply Patches
- **After level 2:** Step 4 — Reboot Schedule
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

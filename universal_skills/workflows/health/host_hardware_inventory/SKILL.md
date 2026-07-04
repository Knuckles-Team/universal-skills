---
name: host_hardware_inventory
description: >-
  Parallel execution workflow for host hardware inventory using the Unified Parallel Engine
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
tags: [health, host-hardware-inventory]
concept: CONCEPT:HEALTH-001
---

# Host Hardware Inventory Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for host hardware inventory using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host Cpu
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per host cpu operations for the Host Hardware Inventory workflow.
Expected: `fan_out_per_host_cpu_artifacts`

### Step 2: Gpu
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute gpu operations for the Host Hardware Inventory workflow.
Expected: `gpu_artifacts`

### Step 3: Ram
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute ram operations for the Host Hardware Inventory workflow.
Expected: `ram_artifacts`

### Step 4: Disk
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute disk operations for the Host Hardware Inventory workflow.
Expected: `disk_artifacts`

### Step 5: Kg Ingest [depends_on: fan_out_per_host_cpu, gpu, ram, disk]
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute kg ingest operations for the Host Hardware Inventory workflow.
Expected: `kg_ingest_artifacts`

## Output
- Host Hardware Inventory results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Host Cpu; Step 2 — Gpu; Step 3 — Ram; Step 4 — Disk
- **After level 0:** Step 5 — Kg Ingest

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

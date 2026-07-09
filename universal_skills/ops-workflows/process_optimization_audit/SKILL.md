---
name: process_optimization_audit
description: >-
  Parallel execution workflow for process optimization audit using the Unified Parallel Engine
domain: ops
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
tags: [ops, process-optimization-audit]
concept: CONCEPT:KG-2.12
---

# Process Optimization Audit Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for process optimization audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Process Map Current
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute fan out per process map current operations for the Process Optimization Audit workflow.
Expected: `fan_out_per_process_map_current_artifacts`

### Step 2: Identify Waste [depends_on: fan_out_per_process_map_current]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute identify waste operations for the Process Optimization Audit workflow.
Expected: `identify_waste_artifacts`

### Step 3: Propose Improvements [depends_on: identify_waste]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute propose improvements operations for the Process Optimization Audit workflow.
Expected: `propose_improvements_artifacts`

### Step 4: Roi [depends_on: propose_improvements]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute roi operations for the Process Optimization Audit workflow.
Expected: `roi_artifacts`

### Step 5: KG Persistence [depends_on: roi]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Process Optimization Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Process Map Current
- **After level 0:** Step 2 — Identify Waste
- **After level 1:** Step 3 — Propose Improvements
- **After level 2:** Step 4 — Roi
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

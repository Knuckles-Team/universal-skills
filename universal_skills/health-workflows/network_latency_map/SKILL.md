---
name: network_latency_map
description: >-
  Parallel execution workflow for network latency map using the Unified Parallel Engine
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
tags: [health, network-latency-map]
concept: CONCEPT:HEALTH-001
---

# Network Latency Map Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for network latency map using the Unified Parallel Engine

## Steps

### Step 1: Prerequisites Setup
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute prerequisites setup operations for the Network Latency Map workflow.
Expected: `prerequisites_setup_artifacts`

### Step 2: Parallel Execution [depends_on: prerequisites_setup]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute parallel execution operations for the Network Latency Map workflow.
Expected: `parallel_execution_artifacts`

### Step 3: Verification And Testing [depends_on: parallel_execution]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute verification and testing operations for the Network Latency Map workflow.
Expected: `verification_and_testing_artifacts`

### Step 4: Synthesis And Reporting [depends_on: verification_and_testing]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute synthesis and reporting operations for the Network Latency Map workflow.
Expected: `synthesis_and_reporting_artifacts`

### Step 5: KG Persistence [depends_on: synthesis_and_reporting]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Network Latency Map results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Prerequisites Setup
- **After level 0:** Step 2 — Parallel Execution
- **After level 1:** Step 3 — Verification And Testing
- **After level 2:** Step 4 — Synthesis And Reporting
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

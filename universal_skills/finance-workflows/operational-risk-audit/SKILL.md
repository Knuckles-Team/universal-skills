---
name: operational-risk-audit
skill_type: workflow
description: >-
  Parallel execution workflow for operational risk audit using the Unified Parallel Engine
domain: finance-workflows
agent: quant_analyst
team_config:
  name: quantitative_trading_team
  task_pattern: quantitative analysis and financial computation
  execution_mode: parallel
  specialist_ids:
    - data-fetcher
    - compute-engine
    - risk-assessor
    - report-generator
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
    report-generator: [graph_write, document_tools]
tags: [finance, operational-risk-audit]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.0'
---

# Operational Risk Audit Workflow

**CONCEPT:EE-011**

Parallel execution workflow for operational risk audit using the Unified Parallel Engine

## Steps

### Step 1: Api Uptime
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute api uptime operations for the Operational Risk Audit workflow.
Expected: `api_uptime_artifacts`

### Step 2: Latency
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Execute latency operations for the Operational Risk Audit workflow.
Expected: `latency_artifacts`

### Step 3: Error Rates
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Execute error rates operations for the Operational Risk Audit workflow.
Expected: `error_rates_artifacts`

### Step 4: Failover Test
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Execute failover test operations for the Operational Risk Audit workflow.
Expected: `failover_test_artifacts`

### Step 5: Report [depends_on: api_uptime, latency, error_rates, failover_test]
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Execute report operations for the Operational Risk Audit workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Operational Risk Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Api Uptime; Step 2 — Latency; Step 3 — Error Rates; Step 4 — Failover Test
- **After level 0:** Step 5 — Report
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

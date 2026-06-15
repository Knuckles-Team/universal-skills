---
name: portfolio_stress_test
description: >-
  Aggregates return curves, runs historical crash scenarios, computes rate shock exposures, and compiles risk audits.
domain: finance
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
tags: [stress-test, crash, scenario-analysis, risk]
concept: CONCEPT:EE-011
---

# Portfolio Stress Test Workflow

**CONCEPT:EE-011**

Aggregates return curves, runs historical crash scenarios, computes rate shock exposures, and compiles risk audits.

## Steps

### Step 1: Returns Data Crawlers
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Gathers historical holdings and benchmarks returns data.
Expected: `historical-stress-pricing-data`

### Step 2: Scenario Crash Simulator [depends_on: returns-data-crawlers]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Simulates returns during historical financial crisis events.
Expected: `crisis-returns-scenarios`

### Step 3: Interest Rate Shock [depends_on: returns-data-crawlers]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Applies simulated treasury yield spikes to active pricing metrics.
Expected: `interest-rate-shock-scenarios`

### Step 4: Stress Aggregation [depends_on: scenario-crash-simulator, interest-rate-shock]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Aggregates stress-test drawdowns into a compliance card.
Expected: `stress-metrics-scorecard`

### Step 5: KG Persistence [depends_on: stress-aggregation]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Portfolio Stress Test results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Returns Data Crawlers
- **After level 0:** Step 2 — Scenario Crash Simulator; Step 3 — Interest Rate Shock
- **After level 1:** Step 4 — Stress Aggregation
- **After level 2:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

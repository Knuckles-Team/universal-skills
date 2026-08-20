---
name: factor-exposure-monitor
skill_type: workflow
description: >-
  Ingest current market data and backtest a supplied, already-defined factor set
  with Qlib to surface the portfolio's present exposure to those factors. Use
  when a researcher wants an evidence-linked factor-exposure snapshot; this
  workflow does not discover new factors or place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: factor-exposure-monitor-team
  task_pattern: defined-factor exposure snapshot via backtest
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
tags: [finance, factors, risk, monitoring]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Factor Exposure Monitor Workflow

Compose the named atomic skills without adding factor-discovery logic here.

## Inputs

Provide the factor set definition, portfolio/holdings, and date range.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest current
market data for the portfolio's universe.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
supplied factor set to measure exposure.

Expected: `factor_exposure_report`

## Output

Return `factor_exposure_report`. Does not discover new factors or place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

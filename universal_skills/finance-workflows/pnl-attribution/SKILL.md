---
name: pnl-attribution
skill_type: workflow
description: >-
  Ingest market data, backtest a supplied multi-factor strategy with Qlib, and
  render the per-factor performance breakdown in `backtest_report` as a
  formatted attribution document. Use when a researcher wants an evidence-linked
  P&L attribution report; this workflow does not place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: pnl-attribution-team
  task_pattern: multi-factor backtest and P&L attribution report
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - document-converter
tags: [finance, pnl, attribution, reporting]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.1'
  author: Genius
---

# PnL Attribution Workflow

Compose the named atomic skills without adding new attribution math here.

## Inputs

Provide the multi-factor strategy definition, asset universe, and date range.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
multi-factor strategy definition to produce per-factor performance.

Expected: `backtest_report`

### Step 2: document-converter [skill: document-converter] [depends_on: Step 1]

Invoke `$document-converter` with `backtest_report` to render the
per-factor breakdown as a formatted attribution document.

Expected: `attribution_document`

## Output

Return `backtest_report` and `attribution_document`. Does not place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$document-converter`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

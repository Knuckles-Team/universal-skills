---
name: market-regime-report
skill_type: workflow
description: >-
  Ingest market data, backtest a supplied regime-classification factor set with
  Qlib, and render the results as a formatted report. Use when a researcher wants
  an evidence-linked snapshot of the current market regime; this workflow does
  not place trades or guarantee regime persistence.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: market-regime-report-team
  task_pattern: regime-factor backtest and report generation
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - document-converter
tags: [finance, regime, reporting]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.1'
  author: Genius
---

# Market Regime Report Workflow

Compose the named atomic skills without adding forecasting logic here.

## Inputs

Provide the regime-classification factor set, asset universe, and date range.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
regime-classification factor set.

Expected: `regime_backtest_report`

### Step 2: document-converter [skill: document-converter] [depends_on: Step 1]

Invoke `$document-converter` with `regime_backtest_report` to render
it as a formatted Markdown/PDF report.

Expected: `regime_report_document`

## Output

Return `regime_backtest_report` and `regime_report_document`. Does not place
trades or guarantee regime persistence.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$document-converter`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

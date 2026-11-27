---
name: automated-tearsheet
skill_type: workflow
description: >-
  Ingest market data, backtest a supplied strategy definition with Qlib, and render
  the resulting performance metrics as a formatted tearsheet document. Use when a
  researcher wants a repeatable, generated performance report from a single
  strategy backtest; this workflow never places or recommends live trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: automated-tearsheet-team
  task_pattern: single-strategy backtest and tearsheet generation
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - document-converter
tags: [finance, backtesting, reporting]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Automated Tearsheet Workflow

Compose the named atomic skills without adding presentation logic here.

## Inputs

Provide the strategy definition, asset universe, date range, and benchmark.

## Steps

1. Ingest market data by invoking `$quant-data-ingest` with the universe and date range. Verify that `normalized_market_dataset` covers every instrument and the benchmark.
2. Backtest the strategy by invoking `$qlib-backtester` with `normalized_market_dataset` and the strategy definition. Verify that `backtest_report` includes return, drawdown and benchmark-relative metrics.
3. Render the tearsheet by invoking `$document-converter` with `backtest_report`. Verify that `tearsheet_document` exists as Markdown or PDF and shows the same metrics as the report.


### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
strategy definition.

Expected: `backtest_report`

### Step 2: document-converter [skill: document-converter] [depends_on: Step 1]

Invoke `$document-converter` with `backtest_report` to render it as a
formatted Markdown/PDF tearsheet.

Expected: `tearsheet_document`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Dataset misses instruments | Tickers unresolved by the ingest skill | Correct the ticker list in the inputs and re-run Step 0 for the missing names |
| Backtest errors on the strategy | Strategy definition references fields absent from the dataset | Add the required fields to the ingest request or fix the definition, then re-run Step 1 |
| Tearsheet metrics differ from report | Conversion truncated the tables | Re-run `$document-converter` with Markdown output and compare against `backtest_report` |

## Output

Return `backtest_report` and `tearsheet_document`. Do not place or recommend live
trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$document-converter`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

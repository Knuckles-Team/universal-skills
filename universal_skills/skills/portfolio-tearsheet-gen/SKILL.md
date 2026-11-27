---
name: portfolio-tearsheet-gen
skill_type: workflow
description: >-
  Ingest market data for a supplied existing portfolio's holdings, backtest that
  portfolio with Qlib, and render the resulting performance metrics as a
  formatted tearsheet document. Use when a researcher wants a repeatable report
  for an already-held multi-position portfolio, as distinct from a single
  strategy definition; this workflow never places or recommends live trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: portfolio-tearsheet-gen-team
  task_pattern: existing-portfolio backtest and tearsheet generation
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - document-converter
tags: [finance, portfolio, reporting]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Portfolio Tearsheet Generator Workflow

Compose the named atomic skills without adding presentation logic here.

## Inputs

Provide the portfolio holdings (positions and weights), date range, and
benchmark.

## Steps

1. Ingest market data for the holdings and date range with `$quant-data-ingest`. Verify that `normalized_market_dataset` covers every holding for the full range.
2. Backtest the portfolio with `$qlib-backtester` using `normalized_market_dataset`. Verify that `backtest_report` includes performance metrics and the benchmark comparison.
3. Render the report with `$document-converter` into a Markdown or PDF tearsheet. Verify that `tearsheet_document` opens and contains the metrics from `backtest_report`.

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the portfolio's holdings and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
portfolio holdings as the strategy definition.

Expected: `backtest_report`

### Step 2: document-converter [skill: document-converter] [depends_on: Step 1]

Invoke `$document-converter` with `backtest_report` to render it as a
formatted Markdown/PDF tearsheet.

Expected: `tearsheet_document`

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Dataset has gaps for a holding | A ticker is unsupported or delisted | Correct the symbol in the workflow inputs and re-run `$quant-data-ingest` for that holding. |
| Backtest fails to start | The dataset format does not match what `$qlib-backtester` expects | Re-ingest through `$quant-data-ingest` so `normalized_market_dataset` is regenerated, then pass it unchanged. |
| Tearsheet is missing metrics | The converter received an incomplete `backtest_report` | Re-run `$document-converter` with the full `backtest_report` file rather than a summary. |

## Output

Return `backtest_report` and `tearsheet_document`. Do not place or recommend
live trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$document-converter`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

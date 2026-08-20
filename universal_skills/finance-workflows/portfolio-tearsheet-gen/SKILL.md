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
  version: '1.3.0'
  author: Genius
---

# Portfolio Tearsheet Generator Workflow

Compose the named atomic skills without adding presentation logic here.

## Inputs

Provide the portfolio holdings (positions and weights), date range, and
benchmark.

## Steps

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

## Output

Return `backtest_report` and `tearsheet_document`. Do not place or recommend
live trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$document-converter`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

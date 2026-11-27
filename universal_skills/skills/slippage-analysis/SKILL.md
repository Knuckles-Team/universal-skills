---
name: slippage-analysis
skill_type: workflow
description: >-
  Ingest reference market data and execute a supplied strategy via paper trading
  with freqtrade to capture its own fill/slippage report. Use when a researcher
  wants evidence of execution slippage against reference prices for a candidate
  strategy; this workflow only paper-trades and never places live orders.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: slippage-analysis-team
  task_pattern: reference-priced paper execution for slippage evidence
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - freqtrade-executor
tags: [finance, execution, slippage]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Slippage Analysis Workflow

Compose the named atomic skills without adding new slippage math here.

## Inputs

Provide the strategy definition, asset universe, and execution window.

## Steps

1. Ingest reference prices by invoking `$quant-data-ingest` with the strategy universe and window. Verify that `normalized_market_dataset` is returned and non-empty.
2. Paper-trade the strategy by invoking `$freqtrade-executor` with `normalized_market_dataset`. Verify that `execution_report` contains fills with price and slippage fields.
3. Return both artifacts and confirm no live orders were placed. Verify that the freqtrade run was in dry-run mode (`dry_run` true in its config).

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest
reference market prices for the universe and window.

Expected: `normalized_market_dataset`

### Step 1: freqtrade-executor [skill: freqtrade-executor] [depends_on: Step 0]

Invoke `$freqtrade-executor` with `normalized_market_dataset` and the
strategy definition to paper-trade and capture the fill/slippage report.

Expected: `execution_report`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `quant-data-ingest` returns an empty dataset | Universe symbols or window do not match the data source | Check the symbol list and dates in the inputs, fix them, and re-invoke `$quant-data-ingest` with the corrected values. |
| `freqtrade-executor` produces no fills | Strategy never signals inside the window | Widen the execution window or inspect the strategy entry conditions, and re-invoke `$freqtrade-executor`. |
| Run attempts live trading | `dry_run` is false in the freqtrade config | Stop the run, set `dry_run` to true in the config, and restart the paper trade. |

## Output

Return `normalized_market_dataset` and `execution_report`, whose fills carry the
slippage evidence. Only paper-trades; never places live orders.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$freqtrade-executor`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

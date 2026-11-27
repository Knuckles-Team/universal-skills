---
name: qlib-factor-backtest
skill_type: workflow
description: >-
  Ingest market data for a supplied universe and backtest a supplied alpha-factor
  definition with Qlib. Use when a researcher wants a direct, evidence-linked
  backtest of one or more already-defined factors; this workflow does not
  discover new factors or place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: qlib-factor-backtest-team
  task_pattern: direct alpha-factor backtest
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
tags: [finance, backtesting, factors]
concept: CONCEPT:EE-011
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Qlib Factor Backtest Workflow

Compose the named atomic skills without adding factor-discovery logic here.

## Inputs

Provide the factor definition(s), asset universe, and date range.

## Steps

1. Ingest market data for the universe and date range with `$quant-data-ingest`. Verify that `normalized_market_dataset` covers every asset in the universe for the full range.
2. Backtest the supplied factor definitions with `$qlib-backtester` using `normalized_market_dataset`. Verify that `backtest_report` contains performance metrics for each factor.

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
supplied factor definition(s).

Expected: `backtest_report`

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Assets are missing from the dataset | Symbols are unsupported or have no history | Correct the symbols in the inputs and re-run `$quant-data-ingest`. |
| Factor definition fails to evaluate | The expression references a field not in the dataset | Rewrite the factor to use fields listed in `normalized_market_dataset` and re-run `$qlib-backtester`. |
| Report has no results for a factor | The date range is too short for the factor lookback | Extend the date range in the inputs and repeat both steps. |

## Output

Return `backtest_report`. Does not discover new factors or place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

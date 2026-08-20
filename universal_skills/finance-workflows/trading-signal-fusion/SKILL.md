---
name: trading-signal-fusion
skill_type: workflow
description: >-
  Ingest market data and run the TradingAgents swarm debate to vet and fuse a
  supplied set of candidate trading signals, then backtest the fused signal with
  Qlib. Use when a researcher wants evidence-linked fusion of multiple candidate
  signals into one backtested view; this workflow does not place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: trading-signal-fusion-team
  task_pattern: swarm-debated signal fusion and backtest
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - trading-debate
    - qlib-backtester
tags: [finance, signals, backtesting]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Trading Signal Fusion Workflow

Compose the named atomic skills without adding new fusion math here.

## Inputs

Provide the candidate signal definitions, asset universe, and date range.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: trading-debate [skill: trading-debate] [depends_on: Step 0]

Invoke `$trading-debate` with `normalized_market_dataset` and the
candidate signal definitions to vet and fuse them via the TradingAgents swarm
debate.

Expected: `fused_signal_verdict`

### Step 2: qlib-backtester [skill: qlib-backtester] [depends_on: Step 1]

Invoke `$qlib-backtester` with `normalized_market_dataset` and
`fused_signal_verdict` to backtest the fused signal.

Expected: `backtest_report`

## Output

Return `fused_signal_verdict` and `backtest_report`. Does not place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$trading-debate`.
- **After level 1:** Step 2 — `$qlib-backtester`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

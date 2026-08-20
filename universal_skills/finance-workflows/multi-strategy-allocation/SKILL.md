---
name: multi-strategy-allocation
skill_type: workflow
description: >-
  Ingest market data, backtest a supplied set of candidate strategies with Qlib,
  and run the TradingAgents swarm debate to vet the backtested evidence as input
  to an allocation decision. Use when a researcher wants evidence-linked support
  for weighting multiple strategies; this workflow does not execute the
  allocation or place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: multi-strategy-allocation-team
  task_pattern: multi-strategy backtest and vetted allocation evidence
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - trading-debate
tags: [finance, allocation, backtesting]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Multi-Strategy Allocation Workflow

Compose the named atomic skills without adding execution logic here.

## Inputs

Provide the candidate strategy definitions, asset universe, and date range.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and each
candidate strategy definition.

Expected: `strategy_backtest_reports`

### Step 2: trading-debate [skill: trading-debate] [depends_on: Step 1]

Invoke `$trading-debate` with `strategy_backtest_reports` to vet the
relative evidence via the TradingAgents swarm debate.

Expected: `allocation_evidence_verdict`

## Output

Return `strategy_backtest_reports` and `allocation_evidence_verdict`. Does not
execute the allocation or place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$trading-debate`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

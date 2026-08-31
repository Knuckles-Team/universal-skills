---
name: max-drawdown-recovery
skill_type: workflow
description: >-
  Ingest market data, backtest a supplied strategy to surface its maximum-drawdown
  episodes, and run the TradingAgents swarm debate to vet a candidate recovery
  hypothesis for the observed drawdown. Use when a researcher wants
  evidence-linked drawdown analysis and a vetted recovery hypothesis; this
  workflow does not place trades or guarantee recovery.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: max-drawdown-recovery-team
  task_pattern: drawdown backtest and vetted recovery-hypothesis debate
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - qlib-backtester
    - trading-debate
tags: [finance, risk, drawdown]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.1'
  author: Genius
---

# Max Drawdown Recovery Workflow

Compose the named atomic skills without adding execution logic here.

## Inputs

Provide the strategy definition, asset universe, date range, and the candidate
recovery hypothesis to vet.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data for the universe and date range.

Expected: `normalized_market_dataset`

### Step 1: qlib-backtester [skill: qlib-backtester] [depends_on: Step 0]

Invoke `$qlib-backtester` with `normalized_market_dataset` and the
strategy definition to surface drawdown episodes.

Expected: `backtest_report`

### Step 2: trading-debate [skill: trading-debate] [depends_on: Step 1]

Invoke `$trading-debate` with `backtest_report` and the candidate
recovery hypothesis to run the TradingAgents swarm debate.

Expected: `recovery_hypothesis_verdict`

## Output

Return `backtest_report` and `recovery_hypothesis_verdict`. Does not place
trades or guarantee recovery.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$qlib-backtester`.
- **After level 1:** Step 2 — `$trading-debate`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

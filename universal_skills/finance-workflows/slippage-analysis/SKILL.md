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
  version: '1.3.0'
  author: Genius
---

# Slippage Analysis Workflow

Compose the named atomic skills without adding new slippage math here.

## Inputs

Provide the strategy definition, asset universe, and execution window.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest
reference market prices for the universe and window.

Expected: `normalized_market_dataset`

### Step 1: freqtrade-executor [skill: freqtrade-executor] [depends_on: Step 0]

Invoke `$freqtrade-executor` with `normalized_market_dataset` and the
strategy definition to paper-trade and capture the fill/slippage report.

Expected: `execution_report`

## Output

Return `normalized_market_dataset` and `execution_report`, whose fills carry the
slippage evidence. Only paper-trades; never places live orders.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$freqtrade-executor`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: trade-journal-analysis
skill_type: workflow
description: >-
  Execute a supplied strategy via paper trading with freqtrade to produce a trade
  execution log, then profile that log's structure and statistics. Use when a
  researcher wants a structured trade journal ready for review; this workflow
  only paper-trades and never places live orders.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: trade-journal-analysis-team
  task_pattern: paper-trade execution log profiling
  execution_mode: sequential
  specialist_ids:
    - freqtrade-executor
    - dataset-profiler
tags: [finance, execution, journal]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Trade Journal Analysis Workflow

Compose the named atomic skills without adding new journaling logic here.

## Inputs

Provide the strategy definition, asset universe, and execution window.

## Steps

### Step 0: freqtrade-executor [skill: freqtrade-executor]

Invoke `$freqtrade-executor` with the workflow inputs to paper-trade
the strategy and produce a trade execution log.

Expected: `trade_execution_log`

### Step 1: dataset-profiler [skill: dataset-profiler] [depends_on: Step 0]

Invoke `$dataset-profiler` with `trade_execution_log` to produce a
structural and statistical profile.

Expected: `trade_journal_profile`

## Output

Return `trade_execution_log` and `trade_journal_profile`. Only paper-trades;
never places live orders.

## Execution

- **Run first:** Step 0 — `$freqtrade-executor`.
- **After level 0:** Step 1 — `$dataset-profiler`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

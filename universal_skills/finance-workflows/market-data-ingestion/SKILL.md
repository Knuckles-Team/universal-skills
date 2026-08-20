---
name: market-data-ingestion
skill_type: workflow
description: >-
  Ingest quantitative market data for a supplied universe, validate it against a
  declared rule set, and profile its structure. Use when a researcher needs a
  clean, validated market dataset staged for downstream research; this workflow
  does not backtest or place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: market-data-ingestion-team
  task_pattern: validated market-data ingestion and profiling
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - data-quality-auditor
    - dataset-profiler
tags: [finance, data, ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Market Data Ingestion Workflow

Compose the named atomic skills without adding backtest logic here.

## Inputs

Provide the asset universe, date range, and data-quality rule set.

## Steps

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest market
data into the Timeseries Memory backend.

Expected: `normalized_market_dataset`

### Step 1: data-quality-auditor [skill: data-quality-auditor] [depends_on: Step 0]

Invoke `$data-quality-auditor` with `normalized_market_dataset` and
the declared rule set.

Expected: `quality_report`

### Step 2: dataset-profiler [skill: dataset-profiler] [depends_on: Step 1]

Invoke `$dataset-profiler` with `normalized_market_dataset` to produce
a structural and statistical profile.

Expected: `dataset_profile`

## Output

Return `normalized_market_dataset`, `quality_report`, and `dataset_profile`. Does
not backtest or place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$data-quality-auditor`.
- **After level 1:** Step 2 — `$dataset-profiler`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

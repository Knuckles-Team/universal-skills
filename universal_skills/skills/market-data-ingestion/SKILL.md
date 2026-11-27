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
  version: '1.7.0'
  author: Knuckles-Team
---

# Market Data Ingestion Workflow

Compose the named atomic skills without adding backtest logic here.

## Inputs

Provide the asset universe, date range, and data-quality rule set.

## Steps

1. Invoke `$quant-data-ingest` with the asset universe, date range and rule set. Verify that the result contains a non-empty `normalized_market_dataset`.
2. Invoke `$data-quality-auditor` with `normalized_market_dataset` and the declared rule set. Verify that the result contains a non-empty `quality_report`.
3. Invoke `$dataset-profiler` with `normalized_market_dataset`. Verify that the result contains a non-empty `dataset_profile`.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Ingest step returns nothing | The universe, date range or data backend is missing or misspelled | Re-check the workflow inputs against the supplied universe and date range, correct the symbol list, and re-invoke `$quant-data-ingest` with the fixed inputs |
| Quality report flags rule violations | Source data has gaps or out-of-range values | Inspect the failing rows in `quality_report`, narrow the date range or drop the offending symbols, and re-ingest before profiling |
| Profile is empty | The dataset passed in was not the normalized one | Pass `normalized_market_dataset` from Step 0 rather than the raw feed to `$dataset-profiler` |

## Output

Return `normalized_market_dataset`, `quality_report`, and `dataset_profile`. Does
not backtest or place trades.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$data-quality-auditor`.
- **After level 1:** Step 2 — `$dataset-profiler`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

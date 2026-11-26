---
name: feature-store-builder
skill_type: workflow
description: >-
  Ingest market data, validate it, document it as a data dictionary, and profile
  it, producing a curated, documented feature dataset. Use when a researcher
  needs a reusable, documented feature store built from raw market data; this
  workflow does not train or select a model.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: feature-store-builder-team
  task_pattern: curated, documented feature dataset assembly
  execution_mode: sequential
  specialist_ids:
    - quant-data-ingest
    - data-quality-auditor
    - data-dictionary-builder
    - dataset-profiler
tags: [finance, data, feature-store]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Feature Store Builder Workflow

Compose the named atomic skills without adding model-training logic here.

## Inputs

Provide the asset universe, date range, and desired feature fields.

## Steps

1. Ingest raw market data by invoking `$quant-data-ingest` with the universe and date range. Verify that `normalized_market_dataset` is returned with the desired feature fields.
2. Audit quality by invoking `$data-quality-auditor` with the rule set. Verify that `quality_report` lists each rule result.
3. Document fields by invoking `$data-dictionary-builder`. Verify that `feature_data_dictionary` has an entry for every field.
4. Profile the dataset by invoking `$dataset-profiler`. Verify that `feature_profile` includes row counts and summary statistics.

### Step 0: quant-data-ingest [skill: quant-data-ingest]

Invoke `$quant-data-ingest` with the workflow inputs to ingest raw
market data.

Expected: `normalized_market_dataset`

### Step 1: data-quality-auditor [skill: data-quality-auditor] [depends_on: Step 0]

Invoke `$data-quality-auditor` with `normalized_market_dataset` and
the declared rule set.

Expected: `quality_report`

### Step 2: data-dictionary-builder [skill: data-dictionary-builder] [depends_on: Step 1]

Invoke `$data-dictionary-builder` with `normalized_market_dataset` and
`quality_report` to document each field.

Expected: `feature_data_dictionary`

### Step 3: dataset-profiler [skill: dataset-profiler] [depends_on: Step 2]

Invoke `$dataset-profiler` with `normalized_market_dataset` to produce
a structural and statistical profile.

Expected: `feature_profile`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Quality audit fails | Nulls or duplicate rows in the ingested data | Fix them at ingest via `$quant-data-ingest` and rerun the audit. |
| Dictionary misses fields | Feature fields not listed in inputs | Add the fields to the inputs and re-invoke `$data-dictionary-builder`. |
| Request to train a model | Out of scope | Decline, since the workflow only assembles the feature store. |

## Output

Return `normalized_market_dataset`, `feature_data_dictionary`, and
`feature_profile` as the assembled feature store. Does not train or select a model.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$data-quality-auditor`.
- **After level 1:** Step 2 — `$data-dictionary-builder`.
- **After level 2:** Step 3 — `$dataset-profiler`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

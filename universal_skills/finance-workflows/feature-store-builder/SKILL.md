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
  version: '1.3.0'
  author: Genius
---

# Feature Store Builder Workflow

Compose the named atomic skills without adding model-training logic here.

## Inputs

Provide the asset universe, date range, and desired feature fields.

## Steps

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

## Output

Return `normalized_market_dataset`, `feature_data_dictionary`, and
`feature_profile` as the assembled feature store. Does not train or select a model.

## Execution

- **Run first:** Step 0 — `$quant-data-ingest`.
- **After level 0:** Step 1 — `$data-quality-auditor`.
- **After level 1:** Step 2 — `$data-dictionary-builder`.
- **After level 2:** Step 3 — `$dataset-profiler`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

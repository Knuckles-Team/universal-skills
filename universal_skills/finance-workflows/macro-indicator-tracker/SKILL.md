---
name: macro-indicator-tracker
skill_type: workflow
description: >-
  Locate publicly reported macroeconomic indicator releases (CPI, GDP, rates, and
  similar) and ingest them into the Timeseries Memory backend. Use when a
  researcher needs a structured macro-indicator time series as input to another
  pipeline; this workflow does not interpret or forecast regime shifts.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: macro-indicator-tracker-team
  task_pattern: macro-indicator discovery and structured ingestion
  execution_mode: sequential
  specialist_ids:
    - web-search
    - quant-data-ingest
tags: [finance, macro, ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Macro Indicator Tracker Workflow

Compose the named atomic skills without adding interpretation logic here.

## Inputs

Provide the indicator list (e.g. CPI, GDP, policy rate) and the geography/lookback
window.

## Steps

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate the latest
publicly reported releases for the requested indicators.

Expected: `macro_source_packet`

### Step 1: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 0]

Invoke `$quant-data-ingest` with `macro_source_packet` to normalize
the releases into the Timeseries Memory backend.

Expected: `normalized_macro_series`

## Output

Return `normalized_macro_series`. Does not interpret or forecast a regime shift.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$quant-data-ingest`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

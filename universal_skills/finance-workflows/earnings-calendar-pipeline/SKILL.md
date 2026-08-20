---
name: earnings-calendar-pipeline
skill_type: workflow
description: >-
  Locate publicly reported earnings-announcement dates for a supplied ticker
  universe and ingest them into the Timeseries Memory backend. Use when a
  researcher needs a structured earnings calendar as input to another pipeline;
  this workflow does not forecast earnings surprises or trade around them.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: earnings-calendar-pipeline-team
  task_pattern: earnings-date discovery and structured ingestion
  execution_mode: sequential
  specialist_ids:
    - web-search
    - quant-data-ingest
tags: [finance, calendar, ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.0'
  author: Genius
---

# Earnings Calendar Pipeline Workflow

Compose the named atomic skills without adding forecasting logic here.

## Inputs

Provide the ticker universe and the lookahead window.

## Steps

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate publicly
reported earnings-announcement dates for the universe.

Expected: `earnings_date_source_packet`

### Step 1: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 0]

Invoke `$quant-data-ingest` with `earnings_date_source_packet` to
normalize the dates into the Timeseries Memory backend.

Expected: `normalized_earnings_calendar`

## Output

Return `normalized_earnings_calendar`. Does not forecast surprises or trade
around the dates.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$quant-data-ingest`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

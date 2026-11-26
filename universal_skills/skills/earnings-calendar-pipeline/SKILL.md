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
  version: '1.6.2'
  author: Knuckles-Team
---

# Earnings Calendar Pipeline Workflow

Compose the named atomic skills without adding forecasting logic here.

## Inputs

Provide the ticker universe and the lookahead window.

## Steps

1. Locate earnings dates by invoking `$web-search` with the ticker universe and lookahead window. Verify that `earnings_date_source_packet` has a source URL and a date for each ticker found.
2. Normalize the dates by invoking `$quant-data-ingest` with `earnings_date_source_packet`. Verify that `normalized_earnings_calendar` is stored in Timeseries Memory with one row per ticker and date.

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate publicly
reported earnings-announcement dates for the universe.

Expected: `earnings_date_source_packet`

### Step 1: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 0]

Invoke `$quant-data-ingest` with `earnings_date_source_packet` to
normalize the dates into the Timeseries Memory backend.

Expected: `normalized_earnings_calendar`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A ticker has no date in the packet | No public announcement found inside the lookahead window | Widen the lookahead input or search the company investor-relations page via `$web-search`, and otherwise leave the ticker out. |
| Ingest rejects rows | Dates in mixed formats | Normalize the dates to ISO 8601 in `earnings_date_source_packet` and re-invoke `$quant-data-ingest`. |
| Pipeline asked to forecast surprises | Scope creep beyond this workflow | Decline the extra scope, because this workflow only ingests reported dates. |

## Output

Return `normalized_earnings_calendar`. Does not forecast surprises or trade
around the dates.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$quant-data-ingest`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

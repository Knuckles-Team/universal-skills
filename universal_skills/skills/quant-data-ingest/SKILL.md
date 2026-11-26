---
name: quant-data-ingest
domain: finance
skill_type: skill
description: Ingest quantitative trading data via akshare into the Timeseries Memory backend.
metadata:
  version: '1.6.2'
---

# Quant Data Ingest Skill

Use this skill to fetch, normalize, and store high-frequency data using the `akshare` library.

## Workflow

1. Identify the requested asset, timeframe, and macro-indicators.
2. Formulate the `akshare` API call equivalent.
3. Use the `meristem` IntelligenceGraphEngine (via `graph_orchestrate`) to submit an `ingest_akshare` task.
4. Verify the data is flowing into the Time-Series memory abstraction.

## Steps

1. Identify the asset, timeframe and macro indicators requested. Verify that each maps to an `akshare` function by running `python3 -c "import akshare as ak; print(hasattr(ak, '<function>'))"`.
2. Formulate the `akshare` call with symbol, period and date arguments. Verify that a sample call returns a non-empty DataFrame.
3. Submit an `ingest_akshare` task through `graph_orchestrate`. Verify that the call returns a task id.
4. Query the Time-Series memory with `graph_query` for the new data. Verify that a query for the symbol returns rows up to the latest requested date.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `akshare` raises on the call | Function renamed or symbol malformed | Look the function up with `dir(akshare)` and correct the symbol format |
| Task accepted but no data appears | Ingest task failed downstream | Read the task status from `graph_orchestrate` and rerun with a smaller date range |
| Gaps in the series | Source API rate-limited or returned partial data | Fetch the missing window separately and ingest it again |

## Execution
Dispatch the task to the Knowledge Graph using the orchestration engine.

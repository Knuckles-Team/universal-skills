---
name: quant-data-ingest
description: Ingest quantitative trading data via akshare into the Timeseries Memory backend.
---

# Quant Data Ingest Skill

Use this skill to fetch, normalize, and store high-frequency data using the `akshare` library.

## Workflow

1. Identify the requested asset, timeframe, and macro-indicators.
2. Formulate the `akshare` API call equivalent.
3. Use the `agent_utilities` IntelligenceGraphEngine (via `graph_orchestrate`) to submit an `ingest_akshare` task.
4. Verify the data is flowing into the Time-Series memory abstraction.

## Execution
Dispatch the task to the Knowledge Graph using the orchestration engine.

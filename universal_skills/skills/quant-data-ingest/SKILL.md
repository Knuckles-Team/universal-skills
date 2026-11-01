---
name: quant-data-ingest
domain: finance
skill_type: skill
description: Ingest quantitative trading data via akshare into the Timeseries Memory backend.
metadata:
  version: '1.5.2'
---

# Quant Data Ingest Skill

Use this skill to fetch, normalize, and store high-frequency data using the `akshare` library.

## Workflow

1. Identify the requested asset, timeframe, and macro-indicators.
2. Formulate the `akshare` API call equivalent.
3. Submit an `ingest_akshare` task through the arbora ingest operation (`act`; find it with `find(intent="ingest")`).
4. Verify the data is flowing into the Time-Series memory abstraction.

## Execution
Dispatch the task to the Knowledge Graph using the orchestration engine.

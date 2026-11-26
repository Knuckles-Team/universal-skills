---
name: alternative-data-pipeline
skill_type: workflow
description: >-
  Discover, fetch, and normalize non-traditional (web/news-sourced) market-data
  signals by composing the catalog's research and finance atomic skills. Use when
  a quant researcher needs alternative data ingested and quality-checked before
  using it in a factor or backtest pipeline; this workflow does not place trades
  or score signal predictiveness.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: alternative-data-pipeline-team
  task_pattern: alternative-data discovery and quality-checked ingestion
  execution_mode: sequential
  specialist_ids:
    - web-search
    - web-crawler
    - quant-data-ingest
    - data-quality-auditor
tags: [finance, research, alt-data, ingestion]
concept: CONCEPT:EE-011
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Alternative Data Pipeline Workflow

Compose the named atomic skills without adding data-vendor logic here.

## Inputs

Provide the target instruments/universe, alt-data source categories (news, filings,
web-published datasets), lookback window, and any excluded sources.

## Steps

1. Locate candidate sources by invoking `$web-search` with the workflow inputs. Verify that `alt_data_source_packet` lists source URLs within the lookback window and none from the excluded sources.
2. Fetch the full content by invoking `$web-crawler` with `alt_data_source_packet`. Verify that `raw_alt_data_documents` has a non-empty body for each fetched URL.
3. Normalize records by invoking `$quant-data-ingest` with `raw_alt_data_documents`. Verify that `normalized_alt_dataset` carries timestamps and instrument identifiers for the target universe.
4. Check data quality by invoking `$data-quality-auditor` with `normalized_alt_dataset` and the declared rule set. Verify that `quality_report` lists a pass or fail result for every rule.


### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate candidate
alternative-data sources.

Expected: `alt_data_source_packet`

### Step 1: web-crawler [skill: web-crawler] [depends_on: Step 0]

Invoke `$web-crawler` with `alt_data_source_packet` to fetch the full
content of the discovered sources.

Expected: `raw_alt_data_documents`

### Step 2: quant-data-ingest [skill: quant-data-ingest] [depends_on: Step 1]

Invoke `$quant-data-ingest` with `raw_alt_data_documents` and the
workflow inputs to normalize records into the Timeseries Memory backend.

Expected: `normalized_alt_dataset`

### Step 3: data-quality-auditor [skill: data-quality-auditor] [depends_on: Step 2]

Invoke `$data-quality-auditor` with `normalized_alt_dataset` and the
declared rule set.

Expected: `quality_report`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Source packet is empty | Source categories too narrow | Broaden the source categories or lookback window and re-invoke `$web-search` |
| Crawl returns blank pages | Site blocks automated fetches or needs rendering | Drop that URL from the packet and substitute another source from the search results |
| Ingest rejects records | Timestamps or identifiers cannot be parsed | Fix the field mapping given to `$quant-data-ingest` for that source and re-ingest it |
| Quality report fails rules | Duplicates or gaps in the normalized data | Remove duplicates or re-crawl the gap period, then re-run `$data-quality-auditor` |

## Output

Return `normalized_alt_dataset` and `quality_report`. Do not place or recommend
trades from this data alone.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$web-crawler`.
- **After level 1:** Step 2 — `$quant-data-ingest`.
- **After level 2:** Step 3 — `$data-quality-auditor`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

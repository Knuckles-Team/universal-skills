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
  version: '1.3.0'
  author: Genius
---

# Alternative Data Pipeline Workflow

Compose the named atomic skills without adding data-vendor logic here.

## Inputs

Provide the target instruments/universe, alt-data source categories (news, filings,
web-published datasets), lookback window, and any excluded sources.

## Steps

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

## Output

Return `normalized_alt_dataset` and `quality_report`. Do not place or recommend
trades from this data alone.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$web-crawler`.
- **After level 1:** Step 2 — `$quant-data-ingest`.
- **After level 2:** Step 3 — `$data-quality-auditor`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

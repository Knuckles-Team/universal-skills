---
name: news-event-detector
skill_type: workflow
description: >-
  Search and crawl the web for market-relevant news events for a supplied
  universe, then audit the citations for reachability and sourcing. Use when a
  researcher wants a sourced feed of detected news events; this workflow does
  not classify sentiment or place trades.
domain: finance-workflows
license: MIT
requires: []
agent: quant-workflow-orchestrator
team_config:
  name: news-event-detector-team
  task_pattern: sourced news-event discovery and citation audit
  execution_mode: sequential
  specialist_ids:
    - web-search
    - web-crawler
    - citation-auditor
tags: [finance, news, research]
concept: CONCEPT:EE-011
metadata:
  version: '1.3.1'
  author: Genius
---

# News Event Detector Workflow

Compose the named atomic skills without adding sentiment-scoring logic here.

## Inputs

Provide the ticker/universe and the lookback window.

## Steps

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs to locate candidate
news events for the universe.

Expected: `news_source_packet`

### Step 1: web-crawler [skill: web-crawler] [depends_on: Step 0]

Invoke `$web-crawler` with `news_source_packet` to fetch the full
content of the detected articles.

Expected: `raw_news_documents`

### Step 2: citation-auditor [skill: citation-auditor] [depends_on: Step 1]

Invoke `$citation-auditor` with `raw_news_documents` to audit
reachability and sourcing.

Expected: `citation_audit`

## Output

Return `raw_news_documents` and `citation_audit`. Does not classify sentiment or
place trades.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$web-crawler`.
- **After level 1:** Step 2 — `$citation-auditor`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

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
  version: '1.7.0'
  author: Knuckles-Team
---

# News Event Detector Workflow

Compose the named atomic skills without adding sentiment-scoring logic here.

## Inputs

Provide the ticker/universe and the lookback window.

## Steps

1. Invoke `$web-search` with the ticker or universe and lookback window. Verify that the result contains a non-empty `news_source_packet`.
2. Invoke `$web-crawler` with `news_source_packet`. Verify that the result contains a non-empty `raw_news_documents`.
3. Invoke `$citation-auditor` with `raw_news_documents`. Verify that the result contains a non-empty `citation_audit`.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Search returns no events | Lookback window too narrow or ticker misspelled | Widen the lookback window, verify the ticker spelling, and re-invoke `$web-search` |
| Crawler returns empty pages | Source blocks fetching or URL is dead | Drop the unreachable URLs from `news_source_packet` and crawl the remaining sources with `$web-crawler` |
| Citation audit marks sources unreachable | Articles moved or paywalled | Replace the flagged sources with alternatives from the search packet and re-run `$citation-auditor` |

## Output

Return `raw_news_documents` and `citation_audit`. Does not classify sentiment or
place trades.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$web-crawler`.
- **After level 1:** Step 2 — `$citation-auditor`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

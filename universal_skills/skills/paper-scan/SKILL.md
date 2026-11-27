---
name: paper-scan
skill_type: workflow
description: >-
  Parallel execution workflow for paper scan using the Unified Parallel Engine
domain: research-workflows
agent: research_coordinator
team_config:
  name: research_discovery_team
  task_pattern: research discovery and knowledge synthesis
  execution_mode: parallel
  specialist_ids:
    - search-agent
    - analyzer-agent
    - synthesizer-agent
    - ingestor-agent
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
    ingestor-agent: [graph_write, kg_graph_ingest]
tags: [research, scan, arxiv, papers]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.7.0'
---

# Paper Scan Workflow

**CONCEPT:RESEARCH-001**

>-

## Steps

1. Extract topics with `sx_search` and `graph_query`. Verify that a relevance taxonomy is returned.
2. Fetch daily papers with the `scholarx-paper-search` skill and scholarx MCP using the taxonomy. Verify that the paper list is non-empty.
3. Score papers with `graph_analyze`. Verify that each paper has a relevance score.
4. Download top papers with `kg_graph_ingest`. Verify that the downloads appear in `graph_query`.
5. Persist with `graph_write`. Verify that a `graph_query` returns the new nodes.

### Step 1: Topic Extractor
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Extract focus topics from the Knowledge Graph to build a relevance taxonomy.

### Step 2: Scholarx Fetcher
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Fetch daily papers via the scholarx MCP using the extracted taxonomy.

### Step 3: Paper Scorer
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Score the fetched papers locally against the relevance taxonomy.

### Step 4: Paper Downloader
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Bulk download the most valuable papers for ingestion.

### Step 5: KG Persistence [depends_on: paper-downloader]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Empty taxonomy | KG has no focus topics | Pass a hand-written list of focus topics as the taxonomy and re-run Step 2 |
| No papers | Scholarx outage | Check the scholarx MCP health via its status tool and re-run the fetch once it answers |
| Download fails | Paywall | Skip the paper, log its URL in the report, and continue with the remaining downloads via `kg_graph_ingest` |

## Output
- Paper Scan results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Topic Extractor; Step 2 — Scholarx Fetcher; Step 3 — Paper Scorer; Step 4 — Paper Downloader
- **After level 0:** Step 5 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

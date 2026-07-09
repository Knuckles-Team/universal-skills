---
name: paper-scan
skill_type: workflow
description: >-
  >-
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
  version: '1.1.0'
---

# Paper Scan Workflow

**CONCEPT:RESEARCH-001**

>-

## Steps

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

## Output
- Paper Scan results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Topic Extractor; Step 2 — Scholarx Fetcher; Step 3 — Paper Scorer; Step 4 — Paper Downloader
- **After level 0:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

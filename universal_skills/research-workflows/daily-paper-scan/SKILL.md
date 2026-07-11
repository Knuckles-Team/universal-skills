---
name: daily-paper-scan
skill_type: workflow
description: >-
  Parallel execution workflow for daily paper scan using the Unified Parallel Engine
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
tags: [research, daily-paper-scan]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.2.0'
---

# Daily Paper Scan Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for daily paper scan using the Unified Parallel Engine

## Steps

### Step 1: Arxiv
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute arxiv operations for the Daily Paper Scan workflow.
Expected: `arxiv_artifacts`

### Step 2: Pmc
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute pmc operations for the Daily Paper Scan workflow.
Expected: `pmc_artifacts`

### Step 3: Biorxiv
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute biorxiv operations for the Daily Paper Scan workflow.
Expected: `biorxiv_artifacts`

### Step 4: Ssrn
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute ssrn operations for the Daily Paper Scan workflow.
Expected: `ssrn_artifacts`

### Step 5: Score [depends_on: arxiv, pmc, biorxiv, ssrn]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute score operations for the Daily Paper Scan workflow.
Expected: `score_artifacts`

### Step 6: Download Top [depends_on: score]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute download top operations for the Daily Paper Scan workflow.
Expected: `download_top_artifacts`

### Step 7: KG Persistence [depends_on: download_top]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Daily Paper Scan results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Arxiv; Step 2 — Pmc; Step 3 — Biorxiv; Step 4 — Ssrn
- **After level 0:** Step 5 — Score
- **After level 1:** Step 6 — Download Top
- **After level 2:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

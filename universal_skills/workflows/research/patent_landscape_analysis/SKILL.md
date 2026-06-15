---
name: patent_landscape_analysis
description: >-
  Parallel execution workflow for patent landscape analysis using the Unified Parallel Engine
domain: research
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
tags: [research, patent-landscape-analysis]
concept: CONCEPT:RESEARCH-001
---

# Patent Landscape Analysis Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for patent landscape analysis using the Unified Parallel Engine

## Steps

### Step 1: Search Patents
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute search patents operations for the Patent Landscape Analysis workflow.
Expected: `search_patents_artifacts`

### Step 2: Classify [depends_on: search_patents]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute classify operations for the Patent Landscape Analysis workflow.
Expected: `classify_artifacts`

### Step 3: Competitor Mapping [depends_on: classify]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute competitor mapping operations for the Patent Landscape Analysis workflow.
Expected: `competitor_mapping_artifacts`

### Step 4: Report [depends_on: competitor_mapping]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute report operations for the Patent Landscape Analysis workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Patent Landscape Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Search Patents
- **After level 0:** Step 2 — Classify
- **After level 1:** Step 3 — Competitor Mapping
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

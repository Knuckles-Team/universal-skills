---
name: trend-analysis-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for trend analysis pipeline using the Unified Parallel Engine
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
tags: [research, trend-analysis-pipeline]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.1.0'
---

# Trend Analysis Pipeline Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for trend analysis pipeline using the Unified Parallel Engine

## Steps

### Step 1: Collect Publication Counts
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute collect publication counts operations for the Trend Analysis Pipeline workflow.
Expected: `collect_publication_counts_artifacts`

### Step 2: Time Series [depends_on: collect_publication_counts]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute time series operations for the Trend Analysis Pipeline workflow.
Expected: `time_series_artifacts`

### Step 3: Detect Inflection Points [depends_on: time_series]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute detect inflection points operations for the Trend Analysis Pipeline workflow.
Expected: `detect_inflection_points_artifacts`

### Step 4: Report [depends_on: detect_inflection_points]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute report operations for the Trend Analysis Pipeline workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Trend Analysis Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Collect Publication Counts
- **After level 0:** Step 2 — Time Series
- **After level 1:** Step 3 — Detect Inflection Points
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

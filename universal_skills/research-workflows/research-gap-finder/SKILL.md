---
name: research-gap-finder
skill_type: workflow
description: >-
  Parallel execution workflow for research gap finder using the Unified Parallel Engine
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
tags: [research, research-gap-finder]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.1.0'
---

# Research Gap Finder Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for research gap finder using the Unified Parallel Engine

## Steps

### Step 1: Survey Literature
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute survey literature operations for the Research Gap Finder workflow.
Expected: `survey_literature_artifacts`

### Step 2: Identify Gaps [depends_on: survey_literature]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute identify gaps operations for the Research Gap Finder workflow.
Expected: `identify_gaps_artifacts`

### Step 3: Rank By Impact [depends_on: identify_gaps]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute rank by impact operations for the Research Gap Finder workflow.
Expected: `rank_by_impact_artifacts`

### Step 4: Report [depends_on: rank_by_impact]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute report operations for the Research Gap Finder workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Research Gap Finder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Survey Literature
- **After level 0:** Step 2 — Identify Gaps
- **After level 1:** Step 3 — Rank By Impact
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

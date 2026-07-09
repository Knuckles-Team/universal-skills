---
name: author-tracker
description: >-
  Parallel execution workflow for author tracker using the Unified Parallel Engine
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
tags: [research, author-tracker]
concept: CONCEPT:RESEARCH-001
---

# Author Tracker Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for author tracker using the Unified Parallel Engine

## Steps

### Step 1: Publications
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute publications operations for the Author Tracker workflow.
Expected: `publications_artifacts`

### Step 2: H Index [depends_on: publications]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute h index operations for the Author Tracker workflow.
Expected: `h_index_artifacts`

### Step 3: Recent Work [depends_on: h_index]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute recent work operations for the Author Tracker workflow.
Expected: `recent_work_artifacts`

### Step 4: Collaboration Graph [depends_on: recent_work]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute collaboration graph operations for the Author Tracker workflow.
Expected: `collaboration_graph_artifacts`

### Step 5: KG Persistence [depends_on: collaboration_graph]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Author Tracker results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Publications
- **After level 0:** Step 2 — H Index
- **After level 1:** Step 3 — Recent Work
- **After level 2:** Step 4 — Collaboration Graph
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

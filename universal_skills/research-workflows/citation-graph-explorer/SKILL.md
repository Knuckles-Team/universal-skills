---
name: citation-graph-explorer
skill_type: workflow
description: >-
  Parallel execution workflow for citation graph explorer using the Unified Parallel Engine
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
tags: [research, citation-graph-explorer]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.2.0'
---

# Citation Graph Explorer Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for citation graph explorer using the Unified Parallel Engine

## Steps

### Step 1: Seed Paper
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute seed paper operations for the Citation Graph Explorer workflow.
Expected: `seed_paper_artifacts`

### Step 2: Forward Backward Citations [depends_on: seed_paper]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute forward backward citations operations for the Citation Graph Explorer workflow.
Expected: `forward_backward_citations_artifacts`

### Step 3: Cluster [depends_on: forward_backward_citations]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute cluster operations for the Citation Graph Explorer workflow.
Expected: `cluster_artifacts`

### Step 4: Visualize In Kg [depends_on: cluster]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute visualize in kg operations for the Citation Graph Explorer workflow.
Expected: `visualize_in_kg_artifacts`

## Output
- Citation Graph Explorer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Seed Paper
- **After level 0:** Step 2 — Forward Backward Citations
- **After level 1:** Step 3 — Cluster
- **After level 2:** Step 4 — Visualize In Kg

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

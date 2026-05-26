---
name: citation_graph_explorer
description: >-
  Parallel execution workflow for citation graph explorer using the Unified Parallel Engine
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
tags: [research, citation-graph-explorer]
concept: CONCEPT:RESEARCH-001
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

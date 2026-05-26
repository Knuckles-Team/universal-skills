---
name: systematic_review_protocol
description: >-
  Parallel execution workflow for systematic review protocol using the Unified Parallel Engine
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
tags: [research, systematic-review-protocol]
concept: CONCEPT:RESEARCH-001
---

# Systematic Review Protocol Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for systematic review protocol using the Unified Parallel Engine

## Steps

### Step 1: Define Pico
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute define pico operations for the Systematic Review Protocol workflow.
Expected: `define_pico_artifacts`

### Step 2: Search [depends_on: define_pico]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute search operations for the Systematic Review Protocol workflow.
Expected: `search_artifacts`

### Step 3: Screen [depends_on: search]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute screen operations for the Systematic Review Protocol workflow.
Expected: `screen_artifacts`

### Step 4: Extract [depends_on: screen]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute extract operations for the Systematic Review Protocol workflow.
Expected: `extract_artifacts`

### Step 5: Meta Analyze [depends_on: extract]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute meta analyze operations for the Systematic Review Protocol workflow.
Expected: `meta_analyze_artifacts`

### Step 6: KG Persistence [depends_on: meta_analyze]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Systematic Review Protocol results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

---
name: competitive_intelligence_research
description: >-
  Parallel execution workflow for competitive intelligence research using the Unified Parallel Engine
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
tags: [research, competitive-intelligence-research]
concept: CONCEPT:RESEARCH-001
---

# Competitive Intelligence Research Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for competitive intelligence research using the Unified Parallel Engine

## Steps

### Step 1: Products
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute products operations for the Competitive Intelligence Research workflow.
Expected: `products_artifacts`

### Step 2: Patents
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute patents operations for the Competitive Intelligence Research workflow.
Expected: `patents_artifacts`

### Step 3: Papers
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute papers operations for the Competitive Intelligence Research workflow.
Expected: `papers_artifacts`

### Step 4: Hiring
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute hiring operations for the Competitive Intelligence Research workflow.
Expected: `hiring_artifacts`

### Step 5: Swot Report [depends_on: products, patents, papers, hiring]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute swot report operations for the Competitive Intelligence Research workflow.
Expected: `swot_report_artifacts`

### Step 6: KG Persistence [depends_on: swot_report]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Competitive Intelligence Research results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

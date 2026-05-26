---
name: conference_proceedings_scan
description: >-
  Parallel execution workflow for conference proceedings scan using the Unified Parallel Engine
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
tags: [research, conference-proceedings-scan]
concept: CONCEPT:RESEARCH-001
---

# Conference Proceedings Scan Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for conference proceedings scan using the Unified Parallel Engine

## Steps

### Step 1: Neurips
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute neurips operations for the Conference Proceedings Scan workflow.
Expected: `neurips_artifacts`

### Step 2: Icml
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute icml operations for the Conference Proceedings Scan workflow.
Expected: `icml_artifacts`

### Step 3: Iclr
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute iclr operations for the Conference Proceedings Scan workflow.
Expected: `iclr_artifacts`

### Step 4: Extract Key Papers [depends_on: neurips, icml, iclr]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute extract key papers operations for the Conference Proceedings Scan workflow.
Expected: `extract_key_papers_artifacts`

### Step 5: Brief [depends_on: extract_key_papers]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute brief operations for the Conference Proceedings Scan workflow.
Expected: `brief_artifacts`

### Step 6: KG Persistence [depends_on: brief]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Conference Proceedings Scan results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

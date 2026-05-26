---
name: literature_review_builder
description: >-
  Parallel execution workflow for literature review builder using the Unified Parallel Engine
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
tags: [research, literature-review-builder]
concept: CONCEPT:RESEARCH-001
---

# Literature Review Builder Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for literature review builder using the Unified Parallel Engine

## Steps

### Step 1: Define Scope
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute define scope operations for the Literature Review Builder workflow.
Expected: `define_scope_artifacts`

### Step 2: Parallel Search [depends_on: define_scope]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute parallel search operations for the Literature Review Builder workflow.
Expected: `parallel_search_artifacts`

### Step 3: Dedupe [depends_on: parallel_search]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute dedupe operations for the Literature Review Builder workflow.
Expected: `dedupe_artifacts`

### Step 4: Summarize [depends_on: dedupe]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute summarize operations for the Literature Review Builder workflow.
Expected: `summarize_artifacts`

### Step 5: Bibliography [depends_on: summarize]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute bibliography operations for the Literature Review Builder workflow.
Expected: `bibliography_artifacts`

### Step 6: KG Persistence [depends_on: bibliography]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Literature Review Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

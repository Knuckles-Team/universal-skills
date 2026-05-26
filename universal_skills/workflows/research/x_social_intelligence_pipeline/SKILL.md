---
name: x_social_intelligence_pipeline
description: >-
  Parallel execution workflow for x social intelligence pipeline using the Unified Parallel Engine
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
tags: [research, x-social-intelligence-pipeline]
concept: CONCEPT:RESEARCH-001
---

# X Social Intelligence Pipeline Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for x social intelligence pipeline using the Unified Parallel Engine

## Steps

### Step 1: Search X
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute search x operations for the X Social Intelligence Pipeline workflow.
Expected: `search_x_artifacts`

### Step 2: Classify [depends_on: search_x]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute classify operations for the X Social Intelligence Pipeline workflow.
Expected: `classify_artifacts`

### Step 3: Score [depends_on: classify]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute score operations for the X Social Intelligence Pipeline workflow.
Expected: `score_artifacts`

### Step 4: Kg Ingest [depends_on: score]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute kg ingest operations for the X Social Intelligence Pipeline workflow.
Expected: `kg_ingest_artifacts`

### Step 5: Evolution Trigger [depends_on: kg_ingest]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute evolution trigger operations for the X Social Intelligence Pipeline workflow.
Expected: `evolution_trigger_artifacts`

## Output
- X Social Intelligence Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

---
name: multi_domain_survey
description: >-
  Parallel execution workflow for multi domain survey using the Unified Parallel Engine
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
tags: [research, multi-domain-survey]
concept: CONCEPT:RESEARCH-001
---

# Multi Domain Survey Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for multi domain survey using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Domain Cs Ai
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute fan out per domain cs ai operations for the Multi Domain Survey workflow.
Expected: `fan_out_per_domain_cs_ai_artifacts`

### Step 2: Cs Ma
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute cs ma operations for the Multi Domain Survey workflow.
Expected: `cs_ma_artifacts`

### Step 3: Quant Ph
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute quant ph operations for the Multi Domain Survey workflow.
Expected: `quant_ph_artifacts`

### Step 4: Econ
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute econ operations for the Multi Domain Survey workflow.
Expected: `econ_artifacts`

### Step 5: Cross Domain Synthesis [depends_on: fan_out_per_domain_cs_ai, cs_ma, quant_ph, econ]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute cross domain synthesis operations for the Multi Domain Survey workflow.
Expected: `cross_domain_synthesis_artifacts`

### Step 6: KG Persistence [depends_on: cross_domain_synthesis]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Multi Domain Survey results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

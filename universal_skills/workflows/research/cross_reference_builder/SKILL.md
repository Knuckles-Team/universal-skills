---
name: cross_reference_builder
description: >-
  Parallel execution workflow for cross reference builder using the Unified Parallel Engine
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
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
tags: [research, cross-reference-builder]
concept: CONCEPT:RESEARCH-001
---

# Cross Reference Builder Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for cross reference builder using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Concept Find Related Across Pillars
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute fan out per concept find related across pillars operations for the Cross Reference Builder workflow.
Expected: `fan_out_per_concept_find_related_across_pillars_artifacts`

### Step 2: Add Edges [depends_on: fan_out_per_concept_find_related_across_pillars]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute add edges operations for the Cross Reference Builder workflow.
Expected: `add_edges_artifacts`

### Step 3: Report [depends_on: add_edges]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute report operations for the Cross Reference Builder workflow.
Expected: `report_artifacts`

### Step 4: KG Persistence [depends_on: report]
**Agent**: `synthesizer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Reference Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

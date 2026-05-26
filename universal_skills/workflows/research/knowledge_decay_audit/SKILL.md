---
name: knowledge_decay_audit
description: >-
  Parallel execution workflow for knowledge decay audit using the Unified Parallel Engine
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
tags: [research, knowledge-decay-audit]
concept: CONCEPT:RESEARCH-001
---

# Knowledge Decay Audit Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for knowledge decay audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Kg Node Check Freshness
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute fan out per kg node check freshness operations for the Knowledge Decay Audit workflow.
Expected: `fan_out_per_kg_node_check_freshness_artifacts`

### Step 2: Verify Accuracy [depends_on: fan_out_per_kg_node_check_freshness]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute verify accuracy operations for the Knowledge Decay Audit workflow.
Expected: `verify_accuracy_artifacts`

### Step 3: Flag Stale [depends_on: verify_accuracy]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute flag stale operations for the Knowledge Decay Audit workflow.
Expected: `flag_stale_artifacts`

### Step 4: Prune [depends_on: flag_stale]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute prune operations for the Knowledge Decay Audit workflow.
Expected: `prune_artifacts`

## Output
- Knowledge Decay Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

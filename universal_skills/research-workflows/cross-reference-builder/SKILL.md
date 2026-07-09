---
name: cross-reference-builder
skill_type: workflow
description: >-
  Parallel execution workflow for cross reference builder using the Unified Parallel Engine
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
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
tags: [research, cross-reference-builder]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.0.2'
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

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Concept Find Related Across Pillars
- **After level 0:** Step 2 — Add Edges
- **After level 1:** Step 3 — Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

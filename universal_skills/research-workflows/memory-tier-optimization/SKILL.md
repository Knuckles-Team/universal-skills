---
name: memory-tier-optimization
skill_type: workflow
description: >-
  Parallel execution workflow for memory tier optimization using the Unified Parallel Engine
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
    - ingestor-agent
  tool_assignments:
    search-agent: [sx_search, graph_query]
    analyzer-agent: [graph_analyze, sx_storage]
    synthesizer-agent: [graph_analyze, document_tools]
    ingestor-agent: [graph_write, kg_graph_ingest]
tags: [research, memory-tier-optimization]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.0.2'
---

# Memory Tier Optimization Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for memory tier optimization using the Unified Parallel Engine

## Steps

### Step 1: Audit Episodic
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute audit episodic operations for the Memory Tier Optimization workflow.
Expected: `audit_episodic_artifacts`

### Step 2: Promote To Semantic [depends_on: audit_episodic]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute promote to semantic operations for the Memory Tier Optimization workflow.
Expected: `promote_to_semantic_artifacts`

### Step 3: Consolidate Procedural [depends_on: promote_to_semantic]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute consolidate procedural operations for the Memory Tier Optimization workflow.
Expected: `consolidate_procedural_artifacts`

### Step 4: Metrics [depends_on: consolidate_procedural]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute metrics operations for the Memory Tier Optimization workflow.
Expected: `metrics_artifacts`

### Step 5: KG Persistence [depends_on: metrics]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Memory Tier Optimization results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Audit Episodic
- **After level 0:** Step 2 — Promote To Semantic
- **After level 1:** Step 3 — Consolidate Procedural
- **After level 2:** Step 4 — Metrics
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

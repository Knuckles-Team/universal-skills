---
name: ontology_evolution_cycle
description: >-
  Parallel execution workflow for ontology evolution cycle using the Unified Parallel Engine
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
tags: [research, ontology-evolution-cycle]
concept: CONCEPT:RESEARCH-001
---

# Ontology Evolution Cycle Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for ontology evolution cycle using the Unified Parallel Engine

## Steps

### Step 1: Audit Current Ontology
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute audit current ontology operations for the Ontology Evolution Cycle workflow.
Expected: `audit_current_ontology_artifacts`

### Step 2: Find Gaps [depends_on: audit_current_ontology]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute find gaps operations for the Ontology Evolution Cycle workflow.
Expected: `find_gaps_artifacts`

### Step 3: Propose Extensions [depends_on: find_gaps]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute propose extensions operations for the Ontology Evolution Cycle workflow.
Expected: `propose_extensions_artifacts`

### Step 4: Validate [depends_on: propose_extensions]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute validate operations for the Ontology Evolution Cycle workflow.
Expected: `validate_artifacts`

### Step 5: Apply [depends_on: validate]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute apply operations for the Ontology Evolution Cycle workflow.
Expected: `apply_artifacts`

### Step 6: KG Persistence [depends_on: apply]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ontology Evolution Cycle results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Audit Current Ontology
- **After level 0:** Step 2 — Find Gaps
- **After level 1:** Step 3 — Propose Extensions
- **After level 2:** Step 4 — Validate
- **After level 3:** Step 5 — Apply
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

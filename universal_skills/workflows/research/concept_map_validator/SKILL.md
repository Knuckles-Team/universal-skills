---
name: concept_map_validator
description: >-
  Parallel execution workflow for concept map validator using the Unified Parallel Engine
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
tags: [research, concept-map-validator]
concept: CONCEPT:RESEARCH-001
---

# Concept Map Validator Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for concept map validator using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Concept Verify Code Exists
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute fan out per concept verify code exists operations for the Concept Map Validator workflow.
Expected: `fan_out_per_concept_verify_code_exists_artifacts`

### Step 2: Check Docs [depends_on: fan_out_per_concept_verify_code_exists]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute check docs operations for the Concept Map Validator workflow.
Expected: `check_docs_artifacts`

### Step 3: Check Tests [depends_on: check_docs]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute check tests operations for the Concept Map Validator workflow.
Expected: `check_tests_artifacts`

### Step 4: Report Drift [depends_on: check_tests]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute report drift operations for the Concept Map Validator workflow.
Expected: `report_drift_artifacts`

### Step 5: KG Persistence [depends_on: report_drift]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Concept Map Validator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Concept Verify Code Exists
- **After level 0:** Step 2 — Check Docs
- **After level 1:** Step 3 — Check Tests
- **After level 2:** Step 4 — Report Drift
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

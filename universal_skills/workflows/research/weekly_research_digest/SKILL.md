---
name: weekly_research_digest
description: >-
  Parallel execution workflow for weekly research digest using the Unified Parallel Engine
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
tags: [research, weekly-research-digest]
concept: CONCEPT:RESEARCH-001
---

# Weekly Research Digest Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for weekly research digest using the Unified Parallel Engine

## Steps

### Step 1: Scan
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute scan operations for the Weekly Research Digest workflow.
Expected: `scan_artifacts`

### Step 2: Score [depends_on: scan]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute score operations for the Weekly Research Digest workflow.
Expected: `score_artifacts`

### Step 3: Summarize Top Five [depends_on: score]
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute summarize top five operations for the Weekly Research Digest workflow.
Expected: `summarize_top_five_artifacts`

### Step 4: Email Newsletter [depends_on: summarize_top_five]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute email newsletter operations for the Weekly Research Digest workflow.
Expected: `email_newsletter_artifacts`

### Step 5: KG Persistence [depends_on: email_newsletter]
**Agent**: `ingestor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Weekly Research Digest results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan
- **After level 0:** Step 2 — Score
- **After level 1:** Step 3 — Summarize Top Five
- **After level 2:** Step 4 — Email Newsletter
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

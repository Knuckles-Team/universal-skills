---
name: second-brain-sync
skill_type: workflow
description: >-
  Parallel execution workflow for second brain sync using the Unified Parallel Engine
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
tags: [research, second-brain-sync]
concept: CONCEPT:RESEARCH-001
metadata:
  version: '1.1.0'
---

# Second Brain Sync Workflow

**CONCEPT:RESEARCH-001**

Parallel execution workflow for second brain sync using the Unified Parallel Engine

## Steps

### Step 1: Obsidian
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute obsidian operations for the Second Brain Sync workflow.
Expected: `obsidian_artifacts`

### Step 2: Nextcloud
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, sx_storage`

Execute nextcloud operations for the Second Brain Sync workflow.
Expected: `nextcloud_artifacts`

### Step 3: Kg
**Agent**: `synthesizer-agent`
**Tools**: `graph_analyze, document_tools`

Execute kg operations for the Second Brain Sync workflow.
Expected: `kg_artifacts`

### Step 4: Bidirectional Sync [depends_on: obsidian, nextcloud, kg]
**Agent**: `ingestor-agent`
**Tools**: `graph_write, kg_graph_ingest`

Execute bidirectional sync operations for the Second Brain Sync workflow.
Expected: `bidirectional_sync_artifacts`

### Step 5: Dedup [depends_on: bidirectional_sync]
**Agent**: `search-agent`
**Tools**: `sx_search, graph_query`

Execute dedup operations for the Second Brain Sync workflow.
Expected: `dedup_artifacts`

## Output
- Second Brain Sync results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Obsidian; Step 2 — Nextcloud; Step 3 — Kg
- **After level 0:** Step 4 — Bidirectional Sync
- **After level 1:** Step 5 — Dedup

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

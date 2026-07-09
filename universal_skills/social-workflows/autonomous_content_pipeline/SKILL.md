---
name: autonomous_content_pipeline
description: >-
  Parallel execution workflow for autonomous content pipeline using the Unified Parallel Engine
domain: social
agent: content_strategist
team_config:
  name: content_creation_team
  task_pattern: content creation and social media management
  execution_mode: sequential
  specialist_ids:
    - content-creator
    - media-processor
    - publisher-agent
    - analytics-agent
  tool_assignments:
    content-creator: [graph_query, document_tools]
    media-processor: [graph_analyze]
    publisher-agent: [graph_write]
    analytics-agent: [graph_query, graph_analyze]
tags: [social, autonomous-content-pipeline]
concept: CONCEPT:SOCIAL-001
---

# Autonomous Content Pipeline Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for autonomous content pipeline using the Unified Parallel Engine

## Steps

### Step 1: Trend Discovery
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute trend discovery operations for the Autonomous Content Pipeline workflow.
Expected: `trend_discovery_artifacts`

### Step 2: Research [depends_on: trend_discovery]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute research operations for the Autonomous Content Pipeline workflow.
Expected: `research_artifacts`

### Step 3: Script [depends_on: research]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute script operations for the Autonomous Content Pipeline workflow.
Expected: `script_artifacts`

### Step 4: Assets [depends_on: script]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute assets operations for the Autonomous Content Pipeline workflow.
Expected: `assets_artifacts`

### Step 5: Publish [depends_on: assets]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute publish operations for the Autonomous Content Pipeline workflow.
Expected: `publish_artifacts`

### Step 6: KG Persistence [depends_on: publish]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Autonomous Content Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Trend Discovery
- **After level 0:** Step 2 — Research
- **After level 1:** Step 3 — Script
- **After level 2:** Step 4 — Assets
- **After level 3:** Step 5 — Publish
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

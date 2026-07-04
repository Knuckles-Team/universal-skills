---
name: video_content_pipeline
description: >-
  Parallel execution workflow for video content pipeline using the Unified Parallel Engine
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
tags: [social, video-content-pipeline]
concept: CONCEPT:SOCIAL-001
---

# Video Content Pipeline Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for video content pipeline using the Unified Parallel Engine

## Steps

### Step 1: Script
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute script operations for the Video Content Pipeline workflow.
Expected: `script_artifacts`

### Step 2: Assets [depends_on: script]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute assets operations for the Video Content Pipeline workflow.
Expected: `assets_artifacts`

### Step 3: Thumbnail [depends_on: assets]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute thumbnail operations for the Video Content Pipeline workflow.
Expected: `thumbnail_artifacts`

### Step 4: Metadata [depends_on: thumbnail]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute metadata operations for the Video Content Pipeline workflow.
Expected: `metadata_artifacts`

### Step 5: Upload [depends_on: metadata]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute upload operations for the Video Content Pipeline workflow.
Expected: `upload_artifacts`

### Step 6: Promote [depends_on: upload]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute promote operations for the Video Content Pipeline workflow.
Expected: `promote_artifacts`

### Step 7: KG Persistence [depends_on: promote]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Video Content Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Script
- **After level 0:** Step 2 — Assets
- **After level 1:** Step 3 — Thumbnail
- **After level 2:** Step 4 — Metadata
- **After level 3:** Step 5 — Upload
- **After level 4:** Step 6 — Promote
- **After level 5:** Step 7 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

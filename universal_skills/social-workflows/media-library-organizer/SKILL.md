---
name: media-library-organizer
skill_type: workflow
description: >-
  Parallel execution workflow for media library organizer using the Unified Parallel Engine
domain: social-workflows
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
tags: [social, media-library-organizer]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.1.0'
---

# Media Library Organizer Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for media library organizer using the Unified Parallel Engine

## Steps

### Step 1: Scan Library
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute scan library operations for the Media Library Organizer workflow.
Expected: `scan_library_artifacts`

### Step 2: Metadata Extraction [depends_on: scan_library]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute metadata extraction operations for the Media Library Organizer workflow.
Expected: `metadata_extraction_artifacts`

### Step 3: Categorize [depends_on: metadata_extraction]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute categorize operations for the Media Library Organizer workflow.
Expected: `categorize_artifacts`

### Step 4: Dedupe [depends_on: categorize]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute dedupe operations for the Media Library Organizer workflow.
Expected: `dedupe_artifacts`

### Step 5: Report [depends_on: dedupe]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute report operations for the Media Library Organizer workflow.
Expected: `report_artifacts`

### Step 6: KG Persistence [depends_on: report]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Media Library Organizer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Scan Library
- **After level 0:** Step 2 — Metadata Extraction
- **After level 1:** Step 3 — Categorize
- **After level 2:** Step 4 — Dedupe
- **After level 3:** Step 5 — Report
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

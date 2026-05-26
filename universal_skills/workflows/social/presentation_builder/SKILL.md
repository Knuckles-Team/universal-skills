---
name: presentation_builder
description: >-
  Parallel execution workflow for presentation builder using the Unified Parallel Engine
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
tags: [social, presentation-builder]
concept: CONCEPT:SOCIAL-001
---

# Presentation Builder Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for presentation builder using the Unified Parallel Engine

## Steps

### Step 1: Research
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute research operations for the Presentation Builder workflow.
Expected: `research_artifacts`

### Step 2: Outline [depends_on: research]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute outline operations for the Presentation Builder workflow.
Expected: `outline_artifacts`

### Step 3: Generate Slides [depends_on: outline]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute generate slides operations for the Presentation Builder workflow.
Expected: `generate_slides_artifacts`

### Step 4: Design [depends_on: generate_slides]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute design operations for the Presentation Builder workflow.
Expected: `design_artifacts`

### Step 5: Export [depends_on: design]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute export operations for the Presentation Builder workflow.
Expected: `export_artifacts`

### Step 6: KG Persistence [depends_on: export]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Presentation Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

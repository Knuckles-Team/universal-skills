---
name: brand_identity_generator
description: >-
  Parallel execution workflow for brand identity generator using the Unified Parallel Engine
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
tags: [social, brand-identity-generator]
concept: CONCEPT:SOCIAL-001
---

# Brand Identity Generator Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for brand identity generator using the Unified Parallel Engine

## Steps

### Step 1: Logo Concepts
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute logo concepts operations for the Brand Identity Generator workflow.
Expected: `logo_concepts_artifacts`

### Step 2: Color Palette
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute color palette operations for the Brand Identity Generator workflow.
Expected: `color_palette_artifacts`

### Step 3: Typography
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute typography operations for the Brand Identity Generator workflow.
Expected: `typography_artifacts`

### Step 4: Voice Tone
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute voice tone operations for the Brand Identity Generator workflow.
Expected: `voice_tone_artifacts`

### Step 5: Brand Book [depends_on: logo_concepts, color_palette, typography, voice_tone]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute brand book operations for the Brand Identity Generator workflow.
Expected: `brand_book_artifacts`

### Step 6: KG Persistence [depends_on: brand_book]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Brand Identity Generator results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Logo Concepts; Step 2 — Color Palette; Step 3 — Typography; Step 4 — Voice Tone
- **After level 0:** Step 5 — Brand Book
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

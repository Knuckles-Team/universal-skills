---
name: ebook-compiler
skill_type: workflow
description: >-
  Parallel execution workflow for ebook compiler using the Unified Parallel Engine
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
tags: [social, ebook-compiler]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.0.2'
---

# Ebook Compiler Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for ebook compiler using the Unified Parallel Engine

## Steps

### Step 1: Outline
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute outline operations for the Ebook Compiler workflow.
Expected: `outline_artifacts`

### Step 2: Parallel Chapter Writing [depends_on: outline]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute parallel chapter writing operations for the Ebook Compiler workflow.
Expected: `parallel_chapter_writing_artifacts`

### Step 3: Edit [depends_on: parallel_chapter_writing]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute edit operations for the Ebook Compiler workflow.
Expected: `edit_artifacts`

### Step 4: Format [depends_on: edit]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute format operations for the Ebook Compiler workflow.
Expected: `format_artifacts`

### Step 5: Epub Export [depends_on: format]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute epub export operations for the Ebook Compiler workflow.
Expected: `epub_export_artifacts`

### Step 6: KG Persistence [depends_on: epub_export]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ebook Compiler results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Outline
- **After level 0:** Step 2 — Parallel Chapter Writing
- **After level 1:** Step 3 — Edit
- **After level 2:** Step 4 — Format
- **After level 3:** Step 5 — Epub Export
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

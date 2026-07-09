---
name: meme-factory-pipeline
skill_type: workflow
description: >-
  Parallel execution workflow for meme factory pipeline using the Unified Parallel Engine
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
tags: [social, meme-factory-pipeline]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.0.2'
---

# Meme Factory Pipeline Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for meme factory pipeline using the Unified Parallel Engine

## Steps

### Step 1: Trend Scan
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute trend scan operations for the Meme Factory Pipeline workflow.
Expected: `trend_scan_artifacts`

### Step 2: Template Select [depends_on: trend_scan]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute template select operations for the Meme Factory Pipeline workflow.
Expected: `template_select_artifacts`

### Step 3: Generate Variants [depends_on: template_select]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute generate variants operations for the Meme Factory Pipeline workflow.
Expected: `generate_variants_artifacts`

### Step 4: A B Test [depends_on: generate_variants]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute a b test operations for the Meme Factory Pipeline workflow.
Expected: `a_b_test_artifacts`

### Step 5: Post [depends_on: a_b_test]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute post operations for the Meme Factory Pipeline workflow.
Expected: `post_artifacts`

### Step 6: KG Persistence [depends_on: post]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Meme Factory Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Trend Scan
- **After level 0:** Step 2 — Template Select
- **After level 1:** Step 3 — Generate Variants
- **After level 2:** Step 4 — A B Test
- **After level 3:** Step 5 — Post
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

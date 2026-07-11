---
name: email-campaign-builder
skill_type: workflow
description: >-
  Parallel execution workflow for email campaign builder using the Unified Parallel Engine
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
tags: [social, email-campaign-builder]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.2.0'
---

# Email Campaign Builder Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for email campaign builder using the Unified Parallel Engine

## Steps

### Step 1: Segment Audience
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute segment audience operations for the Email Campaign Builder workflow.
Expected: `segment_audience_artifacts`

### Step 2: Write Variants [depends_on: segment_audience]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute write variants operations for the Email Campaign Builder workflow.
Expected: `write_variants_artifacts`

### Step 3: A B Test [depends_on: write_variants]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute a b test operations for the Email Campaign Builder workflow.
Expected: `a_b_test_artifacts`

### Step 4: Send [depends_on: a_b_test]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute send operations for the Email Campaign Builder workflow.
Expected: `send_artifacts`

### Step 5: Analyze [depends_on: send]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute analyze operations for the Email Campaign Builder workflow.
Expected: `analyze_artifacts`

### Step 6: KG Persistence [depends_on: analyze]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Email Campaign Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Segment Audience
- **After level 0:** Step 2 — Write Variants
- **After level 1:** Step 3 — A B Test
- **After level 2:** Step 4 — Send
- **After level 3:** Step 5 — Analyze
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: newsletter_automation
description: >-
  Parallel execution workflow for newsletter automation using the Unified Parallel Engine
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
tags: [social, newsletter-automation]
concept: CONCEPT:SOCIAL-001
---

# Newsletter Automation Workflow

**CONCEPT:SOCIAL-001**

Parallel execution workflow for newsletter automation using the Unified Parallel Engine

## Steps

### Step 1: Curate Content
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute curate content operations for the Newsletter Automation workflow.
Expected: `curate_content_artifacts`

### Step 2: Write Digest [depends_on: curate_content]
**Agent**: `media-processor`
**Tools**: `graph_analyze`

Execute write digest operations for the Newsletter Automation workflow.
Expected: `write_digest_artifacts`

### Step 3: Design Template [depends_on: write_digest]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Execute design template operations for the Newsletter Automation workflow.
Expected: `design_template_artifacts`

### Step 4: Send [depends_on: design_template]
**Agent**: `analytics-agent`
**Tools**: `graph_query, graph_analyze`

Execute send operations for the Newsletter Automation workflow.
Expected: `send_artifacts`

### Step 5: Analytics [depends_on: send]
**Agent**: `content-creator`
**Tools**: `graph_query, document_tools`

Execute analytics operations for the Newsletter Automation workflow.
Expected: `analytics_artifacts`

### Step 6: KG Persistence [depends_on: analytics]
**Agent**: `analytics-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Newsletter Automation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Curate Content
- **After level 0:** Step 2 — Write Digest
- **After level 1:** Step 3 — Design Template
- **After level 2:** Step 4 — Send
- **After level 3:** Step 5 — Analytics
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

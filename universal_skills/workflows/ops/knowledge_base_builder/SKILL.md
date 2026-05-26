---
name: knowledge_base_builder
description: >-
  Parallel execution workflow for knowledge base builder using the Unified Parallel Engine
domain: ops
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: [ops, knowledge-base-builder]
concept: CONCEPT:KG-2.12
---

# Knowledge Base Builder Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for knowledge base builder using the Unified Parallel Engine

## Steps

### Step 1: Extract From Resolved Incidents
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute extract from resolved incidents operations for the Knowledge Base Builder workflow.
Expected: `extract_from_resolved_incidents_artifacts`

### Step 2: Draft Articles [depends_on: extract_from_resolved_incidents]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute draft articles operations for the Knowledge Base Builder workflow.
Expected: `draft_articles_artifacts`

### Step 3: Publish [depends_on: draft_articles]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute publish operations for the Knowledge Base Builder workflow.
Expected: `publish_artifacts`

### Step 4: KG Persistence [depends_on: publish]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Knowledge Base Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

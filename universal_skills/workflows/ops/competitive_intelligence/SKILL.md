---
name: competitive_intelligence
description: >-
  Parallel execution workflow for competitive intelligence using the Unified Parallel Engine
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
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, competitive-intelligence]
concept: CONCEPT:KG-2.12
---

# Competitive Intelligence Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for competitive intelligence using the Unified Parallel Engine

## Steps

### Step 1: Pricing
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute pricing operations for the Competitive Intelligence workflow.
Expected: `pricing_artifacts`

### Step 2: Features
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute features operations for the Competitive Intelligence workflow.
Expected: `features_artifacts`

### Step 3: Hiring
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute hiring operations for the Competitive Intelligence workflow.
Expected: `hiring_artifacts`

### Step 4: News
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute news operations for the Competitive Intelligence workflow.
Expected: `news_artifacts`

### Step 5: Dashboard [depends_on: pricing, features, hiring, news]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute dashboard operations for the Competitive Intelligence workflow.
Expected: `dashboard_artifacts`

### Step 6: KG Persistence [depends_on: dashboard]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Competitive Intelligence results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

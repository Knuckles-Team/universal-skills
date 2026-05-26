---
name: release_notes_aggregation
description: >-
  Parallel execution workflow for release notes aggregation using the Unified Parallel Engine
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
tags: [ops, release-notes-aggregation]
concept: CONCEPT:KG-2.12
---

# Release Notes Aggregation Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for release notes aggregation using the Unified Parallel Engine

## Steps

### Step 1: Jira Tickets
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute jira tickets operations for the Release Notes Aggregation workflow.
Expected: `jira_tickets_artifacts`

### Step 2: Prs
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute prs operations for the Release Notes Aggregation workflow.
Expected: `prs_artifacts`

### Step 3: Commits
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute commits operations for the Release Notes Aggregation workflow.
Expected: `commits_artifacts`

### Step 4: Aggregate [depends_on: jira_tickets, prs, commits]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute aggregate operations for the Release Notes Aggregation workflow.
Expected: `aggregate_artifacts`

### Step 5: Publish [depends_on: aggregate]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute publish operations for the Release Notes Aggregation workflow.
Expected: `publish_artifacts`

### Step 6: KG Persistence [depends_on: publish]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Release Notes Aggregation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

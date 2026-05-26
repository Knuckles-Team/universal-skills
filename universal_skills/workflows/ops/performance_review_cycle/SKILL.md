---
name: performance_review_cycle
description: >-
  Parallel execution workflow for performance review cycle using the Unified Parallel Engine
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
tags: [ops, performance-review-cycle]
concept: CONCEPT:KG-2.12
---

# Performance Review Cycle Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for performance review cycle using the Unified Parallel Engine

## Steps

### Step 1: Collect Metrics
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute collect metrics operations for the Performance Review Cycle workflow.
Expected: `collect_metrics_artifacts`

### Step 2: Peer Feedback [depends_on: collect_metrics]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute peer feedback operations for the Performance Review Cycle workflow.
Expected: `peer_feedback_artifacts`

### Step 3: Draft Review [depends_on: peer_feedback]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute draft review operations for the Performance Review Cycle workflow.
Expected: `draft_review_artifacts`

### Step 4: Schedule [depends_on: draft_review]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute schedule operations for the Performance Review Cycle workflow.
Expected: `schedule_artifacts`

### Step 5: KG Persistence [depends_on: schedule]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Performance Review Cycle results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

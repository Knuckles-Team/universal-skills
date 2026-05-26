---
name: customer_feedback_analysis
description: >-
  Parallel execution workflow for customer feedback analysis using the Unified Parallel Engine
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
tags: [ops, customer-feedback-analysis]
concept: CONCEPT:KG-2.12
---

# Customer Feedback Analysis Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for customer feedback analysis using the Unified Parallel Engine

## Steps

### Step 1: Support Tickets
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute support tickets operations for the Customer Feedback Analysis workflow.
Expected: `support_tickets_artifacts`

### Step 2: Reviews
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute reviews operations for the Customer Feedback Analysis workflow.
Expected: `reviews_artifacts`

### Step 3: Surveys
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute surveys operations for the Customer Feedback Analysis workflow.
Expected: `surveys_artifacts`

### Step 4: Sentiment [depends_on: support_tickets, reviews, surveys]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute sentiment operations for the Customer Feedback Analysis workflow.
Expected: `sentiment_artifacts`

### Step 5: Actions [depends_on: sentiment]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute actions operations for the Customer Feedback Analysis workflow.
Expected: `actions_artifacts`

### Step 6: KG Persistence [depends_on: actions]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Customer Feedback Analysis results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

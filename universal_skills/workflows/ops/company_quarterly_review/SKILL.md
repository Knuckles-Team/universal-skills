---
name: company_quarterly_review
description: >-
  Parallel execution workflow for company quarterly review using the Unified Parallel Engine
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
tags: [ops, company-quarterly-review]
concept: CONCEPT:KG-2.12
---

# Company Quarterly Review Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for company quarterly review using the Unified Parallel Engine

## Steps

### Step 1: Each Dept Produces Report
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute each dept produces report operations for the Company Quarterly Review workflow.
Expected: `each_dept_produces_report_artifacts`

### Step 2: Dept Heads Synthesize [depends_on: each_dept_produces_report]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute dept heads synthesize operations for the Company Quarterly Review workflow.
Expected: `dept_heads_synthesize_artifacts`

### Step 3: Ceo Summary [depends_on: dept_heads_synthesize]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute ceo summary operations for the Company Quarterly Review workflow.
Expected: `ceo_summary_artifacts`

### Step 4: KG Persistence [depends_on: ceo_summary]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Company Quarterly Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

---
name: contract_review_pipeline
description: >-
  Parallel execution workflow for contract review pipeline using the Unified Parallel Engine
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
tags: [ops, contract-review-pipeline]
concept: CONCEPT:KG-2.12
---

# Contract Review Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for contract review pipeline using the Unified Parallel Engine

## Steps

### Step 1: Ingest Contract
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute ingest contract operations for the Contract Review Pipeline workflow.
Expected: `ingest_contract_artifacts`

### Step 2: Extract Clauses [depends_on: ingest_contract]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute extract clauses operations for the Contract Review Pipeline workflow.
Expected: `extract_clauses_artifacts`

### Step 3: Risk Analysis [depends_on: extract_clauses]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute risk analysis operations for the Contract Review Pipeline workflow.
Expected: `risk_analysis_artifacts`

### Step 4: Recommend [depends_on: risk_analysis]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute recommend operations for the Contract Review Pipeline workflow.
Expected: `recommend_artifacts`

### Step 5: Summary [depends_on: recommend]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute summary operations for the Contract Review Pipeline workflow.
Expected: `summary_artifacts`

### Step 6: KG Persistence [depends_on: summary]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Contract Review Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

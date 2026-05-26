---
name: m_and_a_due_diligence
description: >-
  Parallel execution workflow for m and a due diligence using the Unified Parallel Engine
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
tags: [ops, m-and-a-due-diligence]
concept: CONCEPT:KG-2.12
---

# M And A Due Diligence Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for m and a due diligence using the Unified Parallel Engine

## Steps

### Step 1: Financial
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute financial operations for the M And A Due Diligence workflow.
Expected: `financial_artifacts`

### Step 2: Legal
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute legal operations for the M And A Due Diligence workflow.
Expected: `legal_artifacts`

### Step 3: Technical
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute technical operations for the M And A Due Diligence workflow.
Expected: `technical_artifacts`

### Step 4: Operational
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute operational operations for the M And A Due Diligence workflow.
Expected: `operational_artifacts`

### Step 5: Cultural
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute cultural operations for the M And A Due Diligence workflow.
Expected: `cultural_artifacts`

### Step 6: Synthesis [depends_on: financial, legal, technical, operational, cultural]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute synthesis operations for the M And A Due Diligence workflow.
Expected: `synthesis_artifacts`

### Step 7: KG Persistence [depends_on: synthesis]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- M And A Due Diligence results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

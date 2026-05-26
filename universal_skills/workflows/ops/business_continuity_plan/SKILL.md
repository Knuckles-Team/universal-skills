---
name: business_continuity_plan
description: >-
  Parallel execution workflow for business continuity plan using the Unified Parallel Engine
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
tags: [ops, business-continuity-plan]
concept: CONCEPT:KG-2.12
---

# Business Continuity Plan Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for business continuity plan using the Unified Parallel Engine

## Steps

### Step 1: Risk Assessment
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute risk assessment operations for the Business Continuity Plan workflow.
Expected: `risk_assessment_artifacts`

### Step 2: Recovery Priorities [depends_on: risk_assessment]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute recovery priorities operations for the Business Continuity Plan workflow.
Expected: `recovery_priorities_artifacts`

### Step 3: Procedures [depends_on: recovery_priorities]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute procedures operations for the Business Continuity Plan workflow.
Expected: `procedures_artifacts`

### Step 4: Test [depends_on: procedures]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute test operations for the Business Continuity Plan workflow.
Expected: `test_artifacts`

### Step 5: Update [depends_on: test]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute update operations for the Business Continuity Plan workflow.
Expected: `update_artifacts`

### Step 6: KG Persistence [depends_on: update]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Business Continuity Plan results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

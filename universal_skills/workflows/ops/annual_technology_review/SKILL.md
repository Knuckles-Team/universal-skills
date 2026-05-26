---
name: annual_technology_review
description: >-
  Parallel execution workflow for annual technology review using the Unified Parallel Engine
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
tags: [ops, annual-technology-review]
concept: CONCEPT:KG-2.12
---

# Annual Technology Review Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for annual technology review using the Unified Parallel Engine

## Steps

### Step 1: Evaluate
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute evaluate operations for the Annual Technology Review workflow.
Expected: `evaluate_artifacts`

### Step 2: Compare Alternatives [depends_on: evaluate]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute compare alternatives operations for the Annual Technology Review workflow.
Expected: `compare_alternatives_artifacts`

### Step 3: Migration Plan [depends_on: compare_alternatives]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute migration plan operations for the Annual Technology Review workflow.
Expected: `migration_plan_artifacts`

### Step 4: KG Persistence [depends_on: migration_plan]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Annual Technology Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

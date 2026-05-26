---
name: cross_department_project
description: >-
  Parallel execution workflow for cross department project using the Unified Parallel Engine
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
tags: [ops, cross-department-project]
concept: CONCEPT:KG-2.12
---

# Cross Department Project Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for cross department project using the Unified Parallel Engine

## Steps

### Step 1: Phase 1 Research Parallel
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute phase 1 research parallel operations for the Cross Department Project workflow.
Expected: `phase_1_research_parallel_artifacts`

### Step 2: Phase 2 Impl Parallel [depends_on: phase_1_research_parallel]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute phase 2 impl parallel operations for the Cross Department Project workflow.
Expected: `phase_2_impl_parallel_artifacts`

### Step 3: Phase 3 Qa [depends_on: phase_2_impl_parallel]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute phase 3 qa operations for the Cross Department Project workflow.
Expected: `phase_3_qa_artifacts`

### Step 4: KG Persistence [depends_on: phase_3_qa]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cross Department Project results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

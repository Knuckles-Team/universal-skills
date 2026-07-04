---
name: new_product_launch
description: >-
  Parallel execution workflow for new product launch using the Unified Parallel Engine
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
tags: [ops, new-product-launch]
concept: CONCEPT:KG-2.12
---

# New Product Launch Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for new product launch using the Unified Parallel Engine

## Steps

### Step 1: Research
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute research operations for the New Product Launch workflow.
Expected: `research_artifacts`

### Step 2: Engineering [depends_on: research]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute engineering operations for the New Product Launch workflow.
Expected: `engineering_artifacts`

### Step 3: Marketing [depends_on: research]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute marketing operations for the New Product Launch workflow.
Expected: `marketing_artifacts`

### Step 4: Legal Parallel [depends_on: research]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute legal parallel operations for the New Product Launch workflow.
Expected: `legal_parallel_artifacts`

### Step 5: Launch [depends_on: engineering, marketing, legal_parallel]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute launch operations for the New Product Launch workflow.
Expected: `launch_artifacts`

### Step 6: KG Persistence [depends_on: launch]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- New Product Launch results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Research
- **After level 0:** Step 2 — Engineering; Step 3 — Marketing; Step 4 — Legal Parallel
- **After level 1:** Step 5 — Launch
- **After level 2:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

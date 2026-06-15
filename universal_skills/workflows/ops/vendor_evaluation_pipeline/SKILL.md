---
name: vendor_evaluation_pipeline
description: >-
  Parallel execution workflow for vendor evaluation pipeline using the Unified Parallel Engine
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
tags: [ops, vendor-evaluation-pipeline]
concept: CONCEPT:KG-2.12
---

# Vendor Evaluation Pipeline Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for vendor evaluation pipeline using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Vendor Capabilities
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute fan out per vendor capabilities operations for the Vendor Evaluation Pipeline workflow.
Expected: `fan_out_per_vendor_capabilities_artifacts`

### Step 2: Pricing
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute pricing operations for the Vendor Evaluation Pipeline workflow.
Expected: `pricing_artifacts`

### Step 3: Reviews
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute reviews operations for the Vendor Evaluation Pipeline workflow.
Expected: `reviews_artifacts`

### Step 4: Risk
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute risk operations for the Vendor Evaluation Pipeline workflow.
Expected: `risk_artifacts`

### Step 5: Scorecard [depends_on: fan_out_per_vendor_capabilities, pricing, reviews, risk]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute scorecard operations for the Vendor Evaluation Pipeline workflow.
Expected: `scorecard_artifacts`

### Step 6: KG Persistence [depends_on: scorecard]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Vendor Evaluation Pipeline results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Vendor Capabilities; Step 2 — Pricing; Step 3 — Reviews; Step 4 — Risk
- **After level 0:** Step 5 — Scorecard
- **After level 1:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: company-knowledge-audit
skill_type: workflow
description: >-
  Parallel execution workflow for company knowledge audit using the Unified Parallel Engine
domain: ops-workflows
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
tags: [ops, company-knowledge-audit]
concept: CONCEPT:KG-2.12
metadata:
  version: '1.1.0'
---

# Company Knowledge Audit Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for company knowledge audit using the Unified Parallel Engine

## Steps

### Step 1: Each Dept Audits Their Domain
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute each dept audits their domain operations for the Company Knowledge Audit workflow.
Expected: `each_dept_audits_their_domain_artifacts`

### Step 2: Aggregate [depends_on: each_dept_audits_their_domain]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute aggregate operations for the Company Knowledge Audit workflow.
Expected: `aggregate_artifacts`

### Step 3: Company Report [depends_on: aggregate]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute company report operations for the Company Knowledge Audit workflow.
Expected: `company_report_artifacts`

### Step 4: KG Persistence [depends_on: company_report]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Company Knowledge Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Each Dept Audits Their Domain
- **After level 0:** Step 2 — Aggregate
- **After level 1:** Step 3 — Company Report
- **After level 2:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

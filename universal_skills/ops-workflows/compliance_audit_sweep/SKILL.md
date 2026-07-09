---
name: compliance_audit_sweep
description: >-
  Parallel execution workflow for compliance audit sweep using the Unified Parallel Engine
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
tags: [ops, compliance-audit-sweep]
concept: CONCEPT:KG-2.12
---

# Compliance Audit Sweep Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for compliance audit sweep using the Unified Parallel Engine

## Steps

### Step 1: Gdpr
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute gdpr operations for the Compliance Audit Sweep workflow.
Expected: `gdpr_artifacts`

### Step 2: Soc2
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute soc2 operations for the Compliance Audit Sweep workflow.
Expected: `soc2_artifacts`

### Step 3: Hipaa
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute hipaa operations for the Compliance Audit Sweep workflow.
Expected: `hipaa_artifacts`

### Step 4: Check Controls [depends_on: gdpr, soc2, hipaa]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute check controls operations for the Compliance Audit Sweep workflow.
Expected: `check_controls_artifacts`

### Step 5: Gap Report [depends_on: check_controls]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute gap report operations for the Compliance Audit Sweep workflow.
Expected: `gap_report_artifacts`

### Step 6: KG Persistence [depends_on: gap_report]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Compliance Audit Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Gdpr; Step 2 — Soc2; Step 3 — Hipaa
- **After level 0:** Step 4 — Check Controls
- **After level 1:** Step 5 — Gap Report
- **After level 2:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

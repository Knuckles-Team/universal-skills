---
name: ssl_certificate_sweep
description: >-
  Parallel execution workflow for ssl certificate sweep using the Unified Parallel Engine
domain: health
agent: health_wellness_coordinator
team_config:
  name: health_wellness_team
  task_pattern: health monitoring and wellness optimization
  execution_mode: sequential
  specialist_ids:
    - data-collector
    - analyzer-agent
    - planner-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
tags: [health, ssl-certificate-sweep]
concept: CONCEPT:HEALTH-001
---

# Ssl Certificate Sweep Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for ssl certificate sweep using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Domain Check Expiry
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per domain check expiry operations for the Ssl Certificate Sweep workflow.
Expected: `fan_out_per_domain_check_expiry_artifacts`

### Step 2: Chain Validity
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute chain validity operations for the Ssl Certificate Sweep workflow.
Expected: `chain_validity_artifacts`

### Step 3: Renewal Queue [depends_on: fan_out_per_domain_check_expiry, chain_validity]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute renewal queue operations for the Ssl Certificate Sweep workflow.
Expected: `renewal_queue_artifacts`

### Step 4: KG Persistence [depends_on: renewal_queue]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ssl Certificate Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

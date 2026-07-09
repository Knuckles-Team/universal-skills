---
name: tunnel-health-monitor
skill_type: workflow
description: >-
  Parallel execution workflow for tunnel health monitor using the Unified Parallel Engine
domain: system-workflows
agent: systems_engineer
team_config:
  name: systems_operations_team
  task_pattern: system administration and management
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - analyzer-agent
    - remediator-agent
    - reporter-agent
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
    reporter-agent: [graph_write, document_tools]
tags: [system, tunnel-health-monitor]
concept: CONCEPT:SYS-001
metadata:
  version: '1.0.2'
---

# Tunnel Health Monitor Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for tunnel health monitor using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Tunnel Test Connectivity
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per tunnel test connectivity operations for the Tunnel Health Monitor workflow.
Expected: `fan_out_per_tunnel_test_connectivity_artifacts`

### Step 2: Latency [depends_on: fan_out_per_tunnel_test_connectivity]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute latency operations for the Tunnel Health Monitor workflow.
Expected: `latency_artifacts`

### Step 3: Bandwidth [depends_on: latency]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute bandwidth operations for the Tunnel Health Monitor workflow.
Expected: `bandwidth_artifacts`

### Step 4: Report [depends_on: bandwidth]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute report operations for the Tunnel Health Monitor workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Tunnel Health Monitor results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Tunnel Test Connectivity
- **After level 0:** Step 2 — Latency
- **After level 1:** Step 3 — Bandwidth
- **After level 2:** Step 4 — Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

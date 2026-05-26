---
name: tunnel_health_monitor
description: >-
  Parallel execution workflow for tunnel health monitor using the Unified Parallel Engine
domain: system
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

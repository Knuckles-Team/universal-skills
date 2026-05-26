---
name: network_topology_mapper
description: >-
  Parallel execution workflow for network topology mapper using the Unified Parallel Engine
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
tags: [system, network-topology-mapper]
concept: CONCEPT:SYS-001
---

# Network Topology Mapper Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for network topology mapper using the Unified Parallel Engine

## Steps

### Step 1: Scan Hosts
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute scan hosts operations for the Network Topology Mapper workflow.
Expected: `scan_hosts_artifacts`

### Step 2: Trace Routes [depends_on: scan_hosts]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute trace routes operations for the Network Topology Mapper workflow.
Expected: `trace_routes_artifacts`

### Step 3: Build Graph [depends_on: trace_routes]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute build graph operations for the Network Topology Mapper workflow.
Expected: `build_graph_artifacts`

### Step 4: Kg Ingest [depends_on: build_graph]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute kg ingest operations for the Network Topology Mapper workflow.
Expected: `kg_ingest_artifacts`

### Step 5: Visualize [depends_on: kg_ingest]
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute visualize operations for the Network Topology Mapper workflow.
Expected: `visualize_artifacts`

## Output
- Network Topology Mapper results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

---
name: network_segmentation
description: >-
  Parallel execution workflow for network segmentation using the Unified Parallel Engine
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
tags: [system, network-segmentation]
concept: CONCEPT:SYS-001
---

# Network Segmentation Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for network segmentation using the Unified Parallel Engine

## Steps

### Step 1: Audit Current
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute audit current operations for the Network Segmentation workflow.
Expected: `audit_current_artifacts`

### Step 2: Design Vlans [depends_on: audit_current]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute design vlans operations for the Network Segmentation workflow.
Expected: `design_vlans_artifacts`

### Step 3: Implement [depends_on: design_vlans]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute implement operations for the Network Segmentation workflow.
Expected: `implement_artifacts`

### Step 4: Verify Isolation [depends_on: implement]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute verify isolation operations for the Network Segmentation workflow.
Expected: `verify_isolation_artifacts`

### Step 5: KG Persistence [depends_on: verify_isolation]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Network Segmentation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

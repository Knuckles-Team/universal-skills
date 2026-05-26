---
name: log_rotation_setup
description: >-
  Parallel execution workflow for log rotation setup using the Unified Parallel Engine
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
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
tags: [system, log-rotation-setup]
concept: CONCEPT:SYS-001
---

# Log Rotation Setup Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for log rotation setup using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Service Configure Logrotate
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per service configure logrotate operations for the Log Rotation Setup workflow.
Expected: `fan_out_per_service_configure_logrotate_artifacts`

### Step 2: Test [depends_on: fan_out_per_service_configure_logrotate]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute test operations for the Log Rotation Setup workflow.
Expected: `test_artifacts`

### Step 3: Verify [depends_on: test]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute verify operations for the Log Rotation Setup workflow.
Expected: `verify_artifacts`

### Step 4: KG Persistence [depends_on: verify]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Log Rotation Setup results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

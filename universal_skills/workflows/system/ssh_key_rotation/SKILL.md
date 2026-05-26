---
name: ssh_key_rotation
description: >-
  Parallel execution workflow for ssh key rotation using the Unified Parallel Engine
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
tags: [system, ssh-key-rotation]
concept: CONCEPT:SYS-001
---

# Ssh Key Rotation Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for ssh key rotation using the Unified Parallel Engine

## Steps

### Step 1: Generate New Keys
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute generate new keys operations for the Ssh Key Rotation workflow.
Expected: `generate_new_keys_artifacts`

### Step 2: Distribute [depends_on: generate_new_keys]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute distribute operations for the Ssh Key Rotation workflow.
Expected: `distribute_artifacts`

### Step 3: Update Configs [depends_on: distribute]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute update configs operations for the Ssh Key Rotation workflow.
Expected: `update_configs_artifacts`

### Step 4: Revoke Old [depends_on: update_configs]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute revoke old operations for the Ssh Key Rotation workflow.
Expected: `revoke_old_artifacts`

### Step 5: KG Persistence [depends_on: revoke_old]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ssh Key Rotation results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

---
name: ansible_playbook_runner
description: >-
  Parallel execution workflow for ansible playbook runner using the Unified Parallel Engine
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
tags: [system, ansible-playbook-runner]
concept: CONCEPT:SYS-001
---

# Ansible Playbook Runner Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for ansible playbook runner using the Unified Parallel Engine

## Steps

### Step 1: Inventory Scan
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute inventory scan operations for the Ansible Playbook Runner workflow.
Expected: `inventory_scan_artifacts`

### Step 2: Playbook Select [depends_on: inventory_scan]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute playbook select operations for the Ansible Playbook Runner workflow.
Expected: `playbook_select_artifacts`

### Step 3: Execute [depends_on: playbook_select]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute execute operations for the Ansible Playbook Runner workflow.
Expected: `execute_artifacts`

### Step 4: Verify [depends_on: execute]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute verify operations for the Ansible Playbook Runner workflow.
Expected: `verify_artifacts`

### Step 5: KG Persistence [depends_on: verify]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ansible Playbook Runner results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

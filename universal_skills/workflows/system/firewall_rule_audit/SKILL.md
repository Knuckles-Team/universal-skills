---
name: firewall_rule_audit
description: >-
  Parallel execution workflow for firewall rule audit using the Unified Parallel Engine
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
tags: [system, firewall-rule-audit]
concept: CONCEPT:SYS-001
---

# Firewall Rule Audit Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for firewall rule audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host Dump Iptables
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per host dump iptables operations for the Firewall Rule Audit workflow.
Expected: `fan_out_per_host_dump_iptables_artifacts`

### Step 2: Compare Policy [depends_on: fan_out_per_host_dump_iptables]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute compare policy operations for the Firewall Rule Audit workflow.
Expected: `compare_policy_artifacts`

### Step 3: Report [depends_on: compare_policy]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute report operations for the Firewall Rule Audit workflow.
Expected: `report_artifacts`

### Step 4: KG Persistence [depends_on: report]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Firewall Rule Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

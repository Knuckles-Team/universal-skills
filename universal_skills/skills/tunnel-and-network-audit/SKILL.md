---
name: tunnel-and-network-audit
skill_type: workflow
description: >-
  Audit active SSH tunnels and network connectivity alongside system network interface status.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
tags: ['tunnels', 'network', 'security', 'audit']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.7.0'
---

# Tunnel And Network Audit Workflow

**CONCEPT:INFRA-001**

Audit active SSH tunnels and network connectivity alongside system network interface status.

## Steps

1. List active tunnels with `tun_tm_hosts` and `tun_tm_system`. Verify that the tunnel list is returned.
2. Collect interface stats and connections using the `systems-manager` network tools. Verify that interfaces and connection counts are present.
3. Get the firewall rule summary using the `systems-manager` firewall tool. Verify that the rule list is returned.
4. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: Tunnel Manager
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all active tunnels from the inventory
Expected: `tunnel`

### Step 1: collect-network-statistics [skill: systems-manager]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Show network interface stats and active connections
Expected: `network, interface`

### Step 2: collect-firewall-rules [skill: systems-manager]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Get the system's firewall rules summary
Expected: `firewall, rule`

### Step 3: KG Persistence [depends_on: Step 1, Step 2]
**Agent**: `verifier-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No tunnels listed | Inventory file is empty or missing | Check the inventory path and add the hosts, and list again. |
| Firewall call is denied | Needs elevated privileges | Run with a user allowed to read firewall rules (sudo) and call it again. |
| Host unreachable | SSH down or wrong address | Test with `ssh -v <host>` and correct the inventory entry. |

## Output
- Tunnel And Network Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Tunnel Manager; Step 1 — collect-network-statistics; Step 2 — collect-firewall-rules
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

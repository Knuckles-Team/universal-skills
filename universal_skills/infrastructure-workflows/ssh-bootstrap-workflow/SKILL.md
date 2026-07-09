---
name: ssh-bootstrap-workflow
description: >-
  Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.
domain: infra
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: ['ssh', 'bootstrap', 'keys', 'onboarding', 'security']
concept: CONCEPT:INFRA-001
---

# Ssh Bootstrap Workflow

**CONCEPT:INFRA-001**

Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.

## Steps

### Step 0: Tunnel Manager Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all hosts from the inventory file and check current SSH connectivity status
Expected: `host, inventory, status`

### Step 1: Systems Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Check if SSH keys exist at ~/.ssh/id_rsa. If not, generate a new RSA key pair
Expected: `ssh, key, generate`

### Step 2: Tunnel Manager Mcp
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

For each host that failed connectivity, set up passwordless SSH using the generated key
Expected: `ssh, passwordless, setup`

### Step 3: Tunnel Manager Mcp
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Verify connectivity to all hosts after key distribution
Expected: `verify, connectivity`

### Step 4: KG Persistence [depends_on: tunnel-manager-mcp]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Ssh Bootstrap results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Tunnel Manager Mcp; Step 1 — Systems Manager Mcp; Step 2 — Tunnel Manager Mcp; Step 3 — Tunnel Manager Mcp
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

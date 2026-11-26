---
name: ssh-bootstrap-workflow
skill_type: workflow
description: >-
  Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.
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
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: ['ssh', 'bootstrap', 'keys', 'onboarding', 'security']
concept: CONCEPT:INFRA-001
metadata:
  version: '1.6.2'
---

# Ssh Bootstrap Workflow

**CONCEPT:INFRA-001**

Interactive SSH key bootstrap for new infrastructure hosts. Checks existing connectivity, generates RSA keys if missing, and distributes them via tunnel-manager to establish passwordless SSH access for future discovery scans.

## Steps

1. List hosts and test connectivity with `tun_tm_hosts` and `tun_tm_system`. Verify that each host reports a reachable or failed status.
2. Check for a key with `ls ~/.ssh/id_rsa` and, if absent, generate one with `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa`. Verify that `ls ~/.ssh/id_rsa.pub` lists the public key.
3. Distribute the key to each failed host using the `tunnel-manager-mcp` passwordless SSH setup tool. Verify that the tool reports success for every host.
4. Re-test connectivity with `tun_tm_hosts`. Verify that all hosts now report a connected status.
5. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: inspect-ssh-connectivity [skill: tunnel-manager-mcp]
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all hosts from the inventory file and check current SSH connectivity status
Expected: `host, inventory, status`

### Step 1: Systems Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Check if SSH keys exist at ~/.ssh/id_rsa. If not, generate a new RSA key pair
Expected: `ssh, key, generate`

### Step 2: distribute-ssh-keys [skill: tunnel-manager-mcp]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

For each host that failed connectivity, set up passwordless SSH using the generated key
Expected: `ssh, passwordless, setup`

### Step 3: verify-ssh-connectivity [skill: tunnel-manager-mcp]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Verify connectivity to all hosts after key distribution
Expected: `verify, connectivity`

### Step 4: KG Persistence [depends_on: Step 0, Step 2, Step 3]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Key distribution fails with permission denied | Initial password or user is wrong | Confirm the username and password for the host, and re-run the distribution for that host. |
| Host stays unreachable | Host is down or port 22 is blocked | Check with `ssh -v <host>` and open the firewall or fix the inventory address. |
| `ssh-keygen` prompts for overwrite | Key already exists | Keep the existing key and skip generation, or use a new path with `-f`. |

## Output
- Ssh Bootstrap results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — inspect-ssh-connectivity; Step 1 — Systems Manager Mcp; Step 2 — distribute-ssh-keys; Step 3 — verify-ssh-connectivity
- **After level 0:** Step 4 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

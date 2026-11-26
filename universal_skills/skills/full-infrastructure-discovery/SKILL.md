---
name: full-infrastructure-discovery
skill_type: workflow
description: Full self-hosted or enterprise infrastructure discovery pipeline. Scans an AgentConfig-managed inventory via tunnel-manager, discovers containers via configured runtime providers, maps networking and DNS, and ingests a privacy-safe topology snapshot into the Knowledge Graph. Use for a governed fleet topology refresh; do not use for ad hoc host probing.
domain: infrastructure-workflows
tags: ['discovery', 'topology', 'inventory', 'self-hosted', 'enterprise']
requires: ['tunnel-manager-mcp', 'container-manager-mcp', 'portainer-mcp', 'technitium-dns-mcp']
metadata:
  version: '1.6.2'
---

# full-infrastructure-discovery Workflow

Discover a self-hosted or enterprise deployment from AgentConfig connection
references and ingest a privacy-safe topology snapshot. Environment topology stays
in the configured providers rather than this workflow.

### Step 0: discover-hosts [skill: tunnel-manager-mcp]
List all hosts from inventory and check SSH connectivity
Expected: host, inventory, connectivity

### Step 1: container-manager-mcp
List all containers across all discovered hosts with their images, status, ports, and networks
Expected: container, image, status
Depends On: Step 0

### Step 2: portainer-mcp
List all Portainer environments and stacks with their deployment status
Expected: environment, stack, endpoint

### Step 3: scan-host-networks [skill: tunnel-manager-mcp]
Run network interface scan across all hosts to discover subnets, VLANs, and VPN tunnels
Expected: network, interface, subnet
Depends On: Step 0

### Step 4: technitium-dns-mcp
List all DNS records to map domain-to-service routing
Expected: record, domain

### Step 5: arbora
Ingest discovered topology into the Knowledge Graph as HardwareNode, Container, ContainerStack, NetworkSubnet, DNSRecord nodes with RUNS_ON, BELONGS_TO_STACK, RESOLVES_DNS_FOR relationships
Expected: ingest, node, relationship
Depends On: Step 1, Step 2, Step 3, Step 4

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — discover-hosts; Step 1 — container-manager-mcp; Step 2 — portainer-mcp; Step 3 — scan-host-networks; Step 4 — technitium-dns-mcp; Step 5 — arbora

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

## Steps

1. Confirm the providers are reachable by checking that `tunnel-manager-mcp`, `container-manager-mcp`, `portainer-mcp` and `technitium-dns-mcp` are listed in `requires` with `grep -n "^requires" SKILL.md`. Verify that each server answers a list call before starting.
2. Run Step 0 and Step 3 with `tunnel-manager-mcp` to list hosts and scan networks. Verify that the host list is non-empty and each host reports SSH connectivity.
3. Run Steps 1, 2 and 4 against the discovered hosts to collect containers, Portainer stacks and DNS records with `container-manager-mcp`, `portainer-mcp` and `technitium-dns-mcp`. Verify that each result contains the Expected fields (container/image/status, environment/stack/endpoint, record/domain).
4. Ingest the snapshot through `graph_orchestrate action=execute_workflow` or the Step 5 arbora call. Verify that a follow-up `graph_query` for `HardwareNode` and `Container` nodes returns the counts discovered in steps 2 and 3.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Host shows SSH unreachable | Inventory entry stale or key not authorized | Fix the AgentConfig connection reference for that host, rerun Step 0 and exclude it only if it is truly decommissioned. |
| Container list empty for a reachable host | Runtime provider not configured for that host | Configure the container runtime profile for the host and rerun Step 1 for that host. |
| Ingest creates no `RUNS_ON` relationships | Step 5 ran before Steps 1 to 4 completed | Rerun the workflow in dependency order so Step 5 starts only after its dependencies have finished. |
| Snapshot contains private addresses or secrets | Raw provider output was ingested unfiltered | Remove the affected nodes and re-ingest after applying the privacy-safe field filter. |

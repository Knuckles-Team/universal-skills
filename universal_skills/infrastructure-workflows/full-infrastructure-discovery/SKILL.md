---
name: full-infrastructure-discovery
skill_type: workflow
description: Full homelab/enterprise discovery pipeline. Scans inventory via tunnel-manager, discovers containers via container-manager and portainer, maps networking and DNS, and ingests everything into the Knowledge Graph as a topology snapshot.
domain: infrastructure-workflows
tags: ['discovery', 'topology', 'inventory', 'homelab', 'enterprise']
requires: ['tunnel-manager-mcp', 'container-manager-mcp', 'portainer-mcp', 'technitium-dns-mcp']
metadata:
  version: '1.1.0'
---

# full-infrastructure-discovery Workflow

Full homelab/enterprise discovery pipeline. Scans inventory via tunnel-manager, discovers containers via container-manager and portainer, maps networking and DNS, and ingests everything into the Knowledge Graph as a topology snapshot.

### Step 0: tunnel-manager-mcp
List all hosts from inventory and check SSH connectivity
Expected: host, inventory, connectivity

### Step 1: container-manager-mcp
List all containers across all discovered hosts with their images, status, ports, and networks
Expected: container, image, status
Depends On: Step 0

### Step 2: portainer-mcp
List all Portainer environments and stacks with their deployment status
Expected: environment, stack, endpoint

### Step 3: tunnel-manager-mcp
Run network interface scan across all hosts to discover subnets, VLANs, and VPN tunnels
Expected: network, interface, subnet
Depends On: Step 0

### Step 4: technitium-dns-mcp
List all DNS records to map domain-to-service routing
Expected: record, domain

### Step 5: graph-os
Ingest discovered topology into the Knowledge Graph as HardwareNode, Container, ContainerStack, NetworkSubnet, DNSRecord nodes with RUNS_ON, BELONGS_TO_STACK, RESOLVES_DNS_FOR relationships
Expected: ingest, node, relationship
Depends On: Step 1, Step 2, Step 3, Step 4

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — tunnel-manager-mcp; Step 1 — container-manager-mcp; Step 2 — portainer-mcp; Step 3 — tunnel-manager-mcp; Step 4 — technitium-dns-mcp; Step 5 — graph-os

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: infrastructure-orchestrator
description: >
  Native, graph-driven infrastructure discovery, topology mapping, and platform
  deployment for homelab and enterprise environments — as a grouping of atomic
  skills. Discovers hardware and network topology, registers authoritative DNS,
  provisions a Docker Swarm mesh, and wires GitOps stack sync, ingesting the full
  topology into the Knowledge Graph. Use when deploying services, scanning
  infrastructure, mapping topology, or managing the homelab. Triggers on "deploy
  platform", "scan infrastructure", "discover topology", "map network", "deploy
  stack", "infrastructure health". Do NOT use for SSH key setup — run ssh-bootstrap
  first if hosts are unreachable.
domain: infra
agent: infrastructure_coordinator
team_config:
  name: infrastructure_orchestration_team
  task_pattern: discover topology, register DNS, provision the swarm, and sync stacks
  execution_mode: dag
  specialist_ids:
    - network-topology-sweep
    - hardware-profile-sweep
    - dns-record-manager
    - swarm-mesh-provisioner
    - portainer-sync-agent
  tool_assignments:
    network-topology-sweep: [tunnel-manager-mcp, systems-manager-mcp]
    hardware-profile-sweep: [systems-manager-mcp, tunnel-manager-mcp]
    dns-record-manager: [technitium-dns-mcp]
    swarm-mesh-provisioner: [container-manager-mcp, tunnel-manager-mcp]
    portainer-sync-agent: [portainer-mcp]
tags: [infra, infrastructure, topology, deployment, swarm, dns, orchestration]
concept: CONCEPT:OS-5.3
---

# Infrastructure Orchestrator Workflow

A skill-workflow that **groups atomic skills** into native, graph-driven
infrastructure orchestration. Each step delegates to a single atomic skill; this
workflow only decides ordering and composition.

## Prerequisites

| MCP Server | Purpose |
|---|---|
| `tunnel-manager-mcp` | SSH inventory, host connectivity, remote execution |
| `container-manager-mcp` | Container runtime discovery (Docker/Podman/K8s) |
| `portainer-mcp` | Stack lifecycle, Swarm management, environment listing |
| `technitium-dns-mcp` | Authoritative DNS server management (→ Caddy picks up `.arpa` domains) |
| `systems-manager-mcp` | OS-level system info, hardware detection |
| `graph-os` | Knowledge Graph ingestion and querying |

If hosts are unreachable, run the **ssh-bootstrap** skill first (native, parallel,
cross-platform full-mesh SSH key distribution) before this workflow.

## Steps

### Step 1: network-topology-sweep
Discover target inventory hosts, verify SSH connectivity, and scan interface
segments, subnets, and VLAN setups across all hardware nodes.
- Requires: `tunnel-manager-mcp`, `systems-manager-mcp`
Expected: discovered active network interfaces and subnet scopes.

### Step 2: hardware-profile-sweep [depends_on: Step 1]
Run low-level hardware resource discovery (CPU models, free RAM, disk partitions,
GPU accelerators) across reachable hosts.
- Requires: `systems-manager-mcp`, `tunnel-manager-mcp`
Expected: system resource specifications and GPUAccelerator profiles.

### Step 3: dns-record-manager [depends_on: Step 1]
Register and manage authoritative zone resolutions and subdomains on the Technitium
DNS primary server.
- Requires: `technitium-dns-mcp`
Expected: authoritative zone DNS mappings.

### Step 4: swarm-mesh-provisioner [depends_on: Step 2]
Initialize Docker Swarm Mode, manage node registrations, and provision the global
overlay network across hosts.
- Requires: `container-manager-mcp`, `tunnel-manager-mcp`
Expected: active multi-node Swarm cluster with cluster-wide overlay networking.

### Step 5: portainer-sync-agent [depends_on: Step 4]
Configure stack synchronizations, deployment pipelines, and GitOps parameters using
PATs.
- Requires: `portainer-mcp`
Expected: sync-configured, containerized platform applications running on the cluster.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on`
run in parallel; dependents run after their prerequisites complete. Each step
invokes the named atomic skill.

- **Run first:** Step 1 — network-topology-sweep
- **After Step 1 (in parallel):** Step 2 — hardware-profile-sweep; Step 3 — dns-record-manager
- **After Step 2:** Step 4 — swarm-mesh-provisioner
- **After Step 4:** Step 5 — portainer-sync-agent

**Execution:** If graph-os is reachable, offload the whole DAG via
`graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill)
for true parallel/swarm execution. Otherwise execute the steps natively in
dependency order: run steps with no unmet `depends_on` in parallel, then their
dependents.

## Topology Map Output

Discovery generates topology maps at `~/.local/share/agent-utilities/topology/`:

```
topology/
├── topology.json           # Full graph (nodes + edges)
├── topology.mermaid.md     # Human-readable Mermaid C4 diagram
├── network_map.json        # Network-only view
├── service_map.json        # Service dependencies
├── last_discovery.json     # Discovery metadata + timestamp
└── snapshots/              # Historical snapshots for diffing
```

## KG Schema Reference

### Node Types (CONCEPT:OS-5.3)

**Compute:** `Container`, `ContainerStack`, `BladeServer`, `GPUAccelerator`
**Networking:** `NetworkSubnet`, `NetworkInterface`, `VPNTunnel`, `FabricSwitch`
**Routing:** `ReverseProxy`, `ProxyRoute`
**DNS:** `DNSService`, `DNSRewrite`
**Observability:** `ObservabilityStack`, `MetricsExporter`
**Registry:** `ContainerRegistry`, `DDClient`
**Enterprise:** `Rack`, `Chassis`, `StorageArray`, `PowerDistribution`, `CoolingUnit`

### Edge Types

**Topology:** `RUNS_ON`, `DEPLOYED_ON`, `BELONGS_TO_STACK`
**Routing:** `ROUTES_TO`, `RESOLVES_DNS_FOR`
**Observability:** `MONITORS`, `EXPORTS_METRICS_TO`
**Networking:** `CONNECTS_VIA`, `HAS_INTERFACE`, `MANAGES_DNS_FOR`
**Enterprise:** `MOUNTED_IN`, `HAS_ACCELERATOR`, `CONNECTED_TO_FABRIC`, `POWERED_BY`, `COOLED_BY`, `ATTACHED_STORAGE`

## OWL Ontology

All infrastructure nodes are BFO-aligned via `ontology_infrastructure.ttl`:
- Imported by the base `ontology.ttl`
- Classes map to BFO upper ontology (IndependentContinuant, Object, Process)
- Object properties define formal topology relationships
- Data properties capture runtime, CIDR, proxy type, VRAM, rack capacity, etc.

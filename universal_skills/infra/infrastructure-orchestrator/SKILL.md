---
name: infrastructure-orchestrator
description: >
  Native infrastructure discovery, topology mapping, and platform deployment
  for homelab and enterprise environments. Discovers hardware via tunnel-manager,
  containers via container-manager/portainer, DNS via technitium-dns, and ingests
  the full topology into the Knowledge Graph. Supports deploying platforms,
  managing DNS records, and wiring observability stacks. Use when deploying
  services, scanning infrastructure, mapping topology, or managing the homelab.
  Triggers on "deploy platform", "scan infrastructure", "discover topology",
  "map network", "deploy stack", "infrastructure health". Do NOT use for SSH
  key setup — use ssh-bootstrap for that.
---

# Infrastructure Orchestrator

Native, graph-driven infrastructure orchestration and discovery system.

## Prerequisites

| MCP Server | Purpose |
|---|---|
| `tunnel-manager-mcp` | SSH inventory, host connectivity, remote execution |
| `container-manager-mcp` | Container runtime discovery (Docker/Podman/K8s) |
| `portainer-mcp` | Stack lifecycle, Swarm management, environment listing |
| `technitium-dns-mcp` | Authoritative DNS server management (→ Caddy picks up `.arpa` domains) |
| `systems-manager-mcp` | OS-level system info, hardware detection |
| `graph-os` | Knowledge Graph ingestion and querying |

### SSH Access Prerequisite

If hosts are unreachable, run the **ssh-bootstrap** skill first to perform a native, parallel, cross-platform full-mesh SSH key distribution:
> See: `infra/ssh-bootstrap/SKILL.md`
> Leverages: `mcp_tm_inventory` -> `mesh_bootstrap` action of the `tunnel-manager-mcp` server.

## Configuration

| Path | Purpose |
|---|---|
| `~/.config/agent-utilities/inventory.yaml` | Canonical host inventory (Ansible format) |
| `~/.config/agent-utilities/config.json` | Agent-utilities config (KG, LLM, telemetry) |
| `~/.config/agent-utilities/mcp_config.json` | MCP server definitions |
| `~/.local/share/agent-utilities/topology/` | Generated topology maps (JSON + Mermaid) |

## Inventory Backends

The inventory supports multiple abstracted backends:

| Backend | Source | Use Case |
|---|---|---|
| **YAML** | `inventory.yaml` | Homelab, small-scale |
| **Ansible Tower** | `ansible-tower-mcp` | Enterprise Ansible |
| **ServiceNow CMDB** | `servicenow-mcp` | Enterprise ITSM |
| **AWS EC2** | AWS API | Cloud infrastructure |

## Steps

### Step 1: network-topology-sweep
Discover target inventory hosts, verify SSH connectivity, and scan interface segments, subnets, and VLAN setups across all hardware nodes:
- Requires: `tunnel-manager-mcp`, `systems-manager-mcp`
- Output: Discovered active network interfaces and subnet scopes.

### Step 2: hardware-profile-sweep [depends_on: network-topology-sweep]
Run low-level hardware resource discovery (CPU models, free RAM capacity, disk partitions, and GPU accelerators) across reachable hosts:
- Requires: `systems-manager-mcp`, `tunnel-manager-mcp`
- Output: System resource specifications and GPUAccelerator profiles.

### Step 3: dns-record-manager [depends_on: network-topology-sweep]
Register and manage authoritative zone resolutions and subdomains on Technitium DNS primary server:
- Requires: `technitium-dns-mcp`
- Output: Authoritative zone DNS mappings.

### Step 4: swarm-mesh-provisioner [depends_on: hardware-profile-sweep]
Initialize Docker Swarm Mode, manage node registrations, and provision global Overlay network across hosts:
- Requires: `container-manager-mcp`, `tunnel-manager-mcp`
- Output: Active multi-node Swarm cluster with cluster-wide overlay networking.

### Step 5: portainer-sync-agent [depends_on: swarm-mesh-provisioner]
Configure stack synchronizations, deployment pipelines, and GitOps parameters using PATs:
- Requires: `portainer-mcp`
- Output: Sync-configured, containerized platform applications running on cluster.


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

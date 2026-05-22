---
name: infrastructure-orchestrator
description: >
  Native infrastructure discovery, topology mapping, and platform deployment
  for homelab and enterprise environments. Discovers hardware via tunnel-manager,
  containers via container-manager/portainer, DNS via adguard-home, and ingests
  the full topology into the Knowledge Graph. Supports deploying platforms,
  managing DNS rewrites, and wiring observability stacks. Use when deploying
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
| `adguard-home-mcp` | DNS rewrite management (→ Traefik picks up `.arpa` domains) |
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

## Workflows

### 1. SSH Bootstrap (Prerequisite)

If hosts lack SSH keys, run the `ssh_bootstrap` workflow first.
This is done in a single highly optimized step using `mcp_tm_inventory(action="mesh_bootstrap", parallel=true)` from `tunnel-manager-mcp`.
See `infra/ssh-bootstrap/SKILL.md` for the interactive and automated flow.

### 2. Full Infrastructure Discovery

Run the `full_infrastructure_discovery` workflow:

```
1. tunnel-manager-mcp → List hosts, check SSH connectivity
2. container-manager-mcp → List all containers (parallel with step 3)
3. portainer-mcp → List all environments and stacks
4. tunnel-manager-mcp → Network interface scan (subnets, VLANs, VPN)
5. adguard-home-mcp → List all DNS rewrites
6. graph-os → Ingest topology into KG
```

**KG nodes created:**
- `HardwareNode` — physical/virtual hosts
- `Container` — runtime-agnostic container instances
- `ContainerStack` — logical stack groupings
- `NetworkSubnet` — discovered network segments
- `NetworkInterface` — per-host NICs
- `DNSRewrite` — domain-to-IP mappings
- `VPNTunnel` — WireGuard/Tailscale tunnels

**KG edges created:**
- `Container -[RUNS_ON]→ HardwareNode`
- `Container -[BELONGS_TO_STACK]→ ContainerStack`
- `DNSRewrite -[RESOLVES_DNS_FOR]→ PlatformService`
- `HardwareNode -[HAS_INTERFACE]→ NetworkInterface`
- `HardwareNode -[CONNECTS_VIA]→ VPNTunnel`

### 3. Hardware Sweep

Run the `hardware_sweep` workflow to collect OS and hardware details:

```
1. tunnel-manager-mcp → List reachable hosts
2. systems-manager-mcp → Collect CPU, RAM, disk, OS info per host
3. systems-manager-mcp → Detect GPU/accelerator hardware
4. graph-os → Update HardwareNode metadata, create GPUAccelerator nodes
```

This data is OWL-native via `ontology_infrastructure.ttl`:
- `HardwareNode` → `bfo:IndependentContinuant`
- `GPUAccelerator` → `bfo:Object`
- `HAS_ACCELERATOR` edge → `:hasAccelerator` object property

### 4. Service Dependency Map

Run `service_dependency_map` to build the full dependency chain:

```
MCPServer → Container → ContainerStack → HardwareNode
ProxyRoute → PlatformService
DNSRewrite → PlatformService
```

### 5. Platform Deployment

Deploy a new platform using the existing `deploy_platform_stack` workflow:

```
1. portainer-mcp → Get endpoint ID
2. portainer-mcp → Create standalone stack from compose file
3. adguard-home-mcp → Create DNS rewrite (*.arpa → host IP)
4. graph-os → Ingest new PlatformService and Container nodes
```

### 6. DNS Management

Create DNS rewrites for new services:

```
adguard-home-mcp → add_rewrite
  domain: "service-name.arpa"
  answer: "10.0.0.10"  # Host IP from inventory
```

Traefik automatically picks up `.arpa` domains via Docker Swarm labels.

### 7. Observability Wiring

| Layer | Tool | Purpose |
|---|---|---|
| **Agent traces** | Langfuse (`langfuse-mcp`) | LLM call tracing, cost tracking |
| **Service metrics** | Prometheus (first-party MCP) | Container/host metrics |
| **Dashboards** | Grafana (first-party MCP) | Visualization |

Install Grafana and Prometheus MCPs via `systems-manager-mcp`.

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

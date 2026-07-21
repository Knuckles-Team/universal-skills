---
name: deployment-planner
skill_type: skill
description: >
  Intelligent service placement and deployment strategy engine for Docker Swarm,
  Kubernetes, or standalone container clusters. Performs hardware discovery,
  service tier classification, compute-weighted placement scoring, and generates
  deterministic deployment blueprints. Produces migration plans with data-aware
  volume handling. Use when deploying services to a new cluster, rebalancing
  existing workloads, capacity planning, or creating golden deployment recipes.
  Triggers on "deployment plan", "rebalance services", "placement strategy",
  "capacity plan", "golden deployment", "where should I put this service",
  "optimize my cluster". Do NOT use for individual container debugging — use
  container-health-check for that.
domain: infrastructure
tags:
  - deployment
  - placement
  - capacity-planning
  - swarm
  - kubernetes
  - optimization
  - blueprint
requires:
  - systems-manager-mcp
  - tunnel-manager-mcp
  - container-manager-mcp
  - portainer-mcp
metadata:
  version: '1.2.1'
---

# Deployment Planner Skill

Deterministic, compute-aware service placement engine for multi-node container clusters.

## Overview

This skill automates the process of determining **which services should run on which hardware nodes** by:
1. Discovering available hardware resources across all cluster nodes
2. Cataloging all deployed (and planned) services with their resource profiles
3. Classifying services into operational tiers with HA requirements
4. Running a placement scoring algorithm to find optimal assignments
5. Generating migration plans including volume data movement
6. Producing a reusable "golden deployment" blueprint

## Prerequisites

| MCP Server | Purpose |
|---|---|
| `systems-manager-mcp` | Hardware resource discovery (CPU, RAM, disk, GPU) |
| `tunnel-manager-mcp` | SSH inventory, cross-host command execution |
| `container-manager-mcp` | Container runtime introspection (Docker/Podman) |
| `portainer-mcp` | Stack lifecycle management, Swarm service updates |
| `graph-os` *(optional)* | Persist placement topology to Knowledge Graph |

## Configuration

| Path | Purpose |
|---|---|
| `~/.config/agent-utilities/inventory.yaml` | Host inventory (Ansible format) |
| Service compose files | Service definitions with resource requirements |
| Docker daemon configs | Registry mirrors, insecure registries |

---

## Steps

### Step 1: Hardware Discovery

Collect compute resources from every reachable node in the cluster inventory.

**Data Collected Per Node:**

| Field | Source Command | Example |
|---|---|---|
| **CPU Model** | `lscpu \| grep "Model name"` | Xeon E5-4620 @ 2.20GHz |
| **CPU Cores** | `nproc` | 64 |
| **RAM Total** | `free -h \| grep Mem` | 247 GiB |
| **RAM Available** | `free -h \| grep Mem` (available column) | 239 GiB |
| **Disk Total/Used** | `df -h /` | 916G total, 626G avail (29%) |
| **GPU/Accelerators** | `nvidia-smi` or `lspci \| grep -i vga` | None / RTX 3090 |
| **Architecture** | `uname -m` | x86_64 / aarch64 |
| **Swarm Role** | `docker node ls` | Leader / Manager / Worker |
| **Node Labels** | `docker node inspect --format labels` | workload-class=general |
| **Container Runtime** | `docker info --format '{{.ServerVersion}}'` | 28.5.1 |

**Output Format:**
```json
{
  "nodes": [
    {
      "hostname": "compute-a",
      "address_ref": "connection://inventory/compute-a",
      "cpu_model": "Example Processor",
      "cpu_cores": 16,
      "ram_total_gib": 64,
      "ram_available_gib": 48,
      "disk_total_gb": 500,
      "disk_available_gb": 350,
      "disk_used_pct": 30,
      "architecture": "x86_64",
      "swarm_role": "leader",
      "labels": {"workload-class": "general"},
      "gpu": null
    }
  ]
}
```

---

### Step 2: Service Catalog

Enumerate all running and configured services with their resource profiles.

**For each service, determine:**

| Field | How to Determine |
|---|---|
| **Name** | Stack name + service name |
| **Image** | `docker service inspect --format image` |
| **Current Node** | `docker service ps --format node` |
| **Replica Count** | `docker service ls --format replicas` |
| **Health Status** | Running / Down (0/1) / Degraded |
| **Networks** | Overlay networks attached |
| **Volumes** | Bind mounts and named volumes |
| **Port Bindings** | Published ports (host-mode vs ingress) |
| **Resource Constraints** | CPU/memory limits from compose |
| **Node Constraint** | `node.labels.name == X` |
| **Dependencies** | Database sidecars, redis, message queues |
| **Storage Affinity** | Needs local NAS mounts? Local bind mounts? |

**Resource Estimation Heuristic:**

When explicit resource limits aren't set, estimate using these defaults:

| Service Type | RAM Estimate | CPU Estimate |
|---|---|---|
| MCP Agent Server | 100-200 MiB | 0.1-0.5 cores |
| Database (PostgreSQL) | 256-512 MiB | 0.5-1.0 cores |
| Redis/Cache | 64-128 MiB | 0.1-0.2 cores |
| Web Application | 256-1024 MiB | 0.5-2.0 cores |
| ML/AI Workload | 2-16 GiB | 2-8 cores |
| Media Server | 1-4 GiB | 2-4 cores |
| Reverse Proxy | 64-256 MiB | 0.2-0.5 cores |
| CI Runner | 512 MiB - 4 GiB | 1-4 cores |
| Observability Stack | 1-8 GiB | 1-4 cores |

---

### Step 3: Service Tier Classification

Classify every service into an operational tier. Tiers determine HA requirements, restart policies, and placement priority.

| Tier | Name | Description | HA Requirement | Placement Priority |
|------|------|-------------|----------------|-------------------|
| **T0** | Critical Infrastructure | DNS, Reverse Proxy, VPN, Container Registry, Swarm management | Must never go down. Pinned to edge/gateway node. | HIGHEST — placed first |
| **T1** | Core Platform | Portainer, GitLab, Auth (Keycloak/OpenBao), Observability (LGTM) | High availability. Multi-node capable. | HIGH |
| **T2** | Business Applications | ERP, Project Management, CRM, Communication | Restart-on-failure. Needs persistent storage. | MEDIUM |
| **T3** | Lifestyle/Utility | Fitness, recipes, genealogy, personal finance, read-later | Best-effort. Restart acceptable. | LOW |
| **T4** | AI/ML & Heavy Compute | LLM inference, speech, transcription, ML training | GPU/ARM affinity. Burst capacity. | MEDIUM (resource-bound) |
| **T5** | Agent MCP Servers | Stateless API bridge containers. Small footprint. | Stateless, trivially restartable. Spread across nodes. | LOW (bulk deploy) |
| **T6** | Media/NAS-Bound | Media servers, arr-suite, downloads, photo management | Must co-locate with storage. Pinned to NAS node. | HIGHEST (storage-bound) |

**Classification Algorithm:**

```
FOR each service:
  IF service.ports includes [53, 80, 443] OR service.name matches [caddy, dns, registry, vpn]:
    tier = T0
  ELIF service.name matches [portainer, gitlab, keycloak, openbao, grafana, loki, prometheus]:
    tier = T1
  ELIF service.name matches [erpnext, plane, twenty, mattermost, nextcloud, paperless]:
    tier = T2
  ELIF service.name matches [mealie, wger, gramps, firefly, calibre, freshrss, archivebox]:
    tier = T3
  ELIF service.image references [ollama, whisper, xtts, immich-ml, stable-diffusion]:
    tier = T4
  ELIF service.name contains "mcp" OR service.image contains "mcp" OR "agent":
    tier = T5
  ELIF service.volumes references NAS paths OR service.name matches [jellyfin, sonarr, radarr, arr]:
    tier = T6
  ELSE:
    tier = T3  # default to lifestyle
```

---

### Step 4: Node Role Assignment

Assign functional roles to each node based on hardware capabilities.

**Role Assignment Rules:**

| Role | Criteria | Responsibilities |
|---|---|---|
| **Gateway/Edge** | Has ports 80/443/53 exposed, runs Caddy/DNS | T0 services, reverse proxy, TLS termination |
| **NAS/Storage** | Has largest/most storage mounts, RAID arrays | T6 services, media servers, NAS-bound |
| **Compute Leader** | Most CPU cores + RAM, Swarm leader | T5 bulk MCP servers, T3 lifestyle, overflow |
| **App Server** | Mid-range, good storage for DBs | T2 business apps, T1 overflow |
| **AI/ML Worker** | GPU present OR ARM with high RAM | T4 inference workloads |

**Auto-detection heuristic:**
```
nodes.sort(by: disk_available, descending)
nas_node = nodes[0] if nodes[0].disk_available > 2x nodes[1].disk_available

nodes.sort(by: cpu_cores * ram_total, descending)
compute_leader = nodes[0]

gateway_node = node where caddy/dns currently runs OR node with lowest latency to WAN

ai_node = node with gpu OR node with architecture == "aarch64" OR highest ram
```

---

### Step 5: Placement Scoring Algorithm

For each service, score candidate nodes and select the optimal placement.

**Scoring Function:**

```
FOR each service S:
  candidates = nodes.filter(compatible_architecture(S))

  IF S.tier == T0: candidates = [gateway_node]          # pinned
  IF S.tier == T6: candidates = [nas_node]               # pinned
  IF S.tier == T4 AND gpu_required: candidates = [ai_node]

  FOR each candidate node N:
    # Base capacity score (0-100)
    ram_headroom = (N.ram_available - S.estimated_ram) / N.ram_total * 100
    cpu_headroom = (N.cpu_cores - N.services_cpu_load) / N.cpu_cores * 100
    disk_headroom = (N.disk_available - S.estimated_disk) / N.disk_total * 100

    capacity_score = min(ram_headroom, cpu_headroom, disk_headroom)

    # Density penalty: prefer spreading services
    density_penalty = N.current_service_count / 20  # penalty increases with density

    # Affinity bonus: co-locate with dependencies
    affinity_bonus = 0
    FOR each dep in S.dependencies:
      IF dep.current_node == N: affinity_bonus += 15

    # Storage bonus: prefer nodes where volumes already exist
    storage_bonus = 0
    IF S.volumes exist on N: storage_bonus += 20

    # Network bonus: same overlay = no cross-node hop
    network_bonus = len(S.networks intersect N.networks) * 5

    FINAL_SCORE = capacity_score - density_penalty + affinity_bonus + storage_bonus + network_bonus

  ASSIGN S to candidate with highest FINAL_SCORE
```

---

### Step 6: Migration Plan Generation

For services that need to move, generate migration commands.

**Migration Types:**

| Type | When | Steps |
|---|---|---|
| **Stateless Move** | MCP servers, proxies, no volumes | Update constraint → redeploy |
| **Volume Move** | Apps with bind-mount data | rsync data → update constraint → redeploy → verify |
| **Database Move** | PostgreSQL, MySQL, MongoDB | pg_dump → rsync → restore → update constraint → verify |

**Stateless Migration Template:**
```bash
# Update service constraint
docker service update --constraint-rm 'node.labels.name == OLD_NODE' \
  --constraint-add 'node.labels.name == NEW_NODE' SERVICE_NAME
```

**Volume Migration Template:**
```bash
# 1. Stop service
docker service scale SERVICE_NAME=0

# 2. Rsync data to target node
rsync -avz --progress OLD_NODE:/path/to/volume/ NEW_NODE:/path/to/volume/

# 3. Update constraint and restart
docker service update --constraint-rm 'node.labels.name == OLD_NODE' \
  --constraint-add 'node.labels.name == NEW_NODE' SERVICE_NAME
docker service scale SERVICE_NAME=1

# 4. Verify
docker service ps SERVICE_NAME --format '{{.Node}} {{.CurrentState}}'
```

---

### Step 7: Blueprint Generation

Generate a deterministic deployment manifest that can recreate the entire cluster.

**Blueprint Format:**
```yaml
# golden-deployment.yaml
cluster:
  name: "example-cluster"
  created: "<ISO-8601-date>"

nodes:
  - hostname: compute-a
    role: compute_leader
    swarm_role: leader
    labels: {workload-class: general}

  - hostname: edge-a
    role: gateway
    swarm_role: worker
    labels: {workload-class: edge}

  - hostname: app-a
    role: app_server
    swarm_role: worker
    labels: {workload-class: application}

placements:
  - service: caddy_caddy
    tier: T0
    node: edge-a
    reason: "Gateway role - reverse proxy with host-mode ports"

  - service: keycloak_keycloak
    tier: T1
    node: edge-a
    reason: "Co-located with Caddy for SSO flows"

networks:
  global:
    - name: caddy
      driver: overlay
      attachable: true
    - name: internet
      driver: overlay
      attachable: true

registry:
  connection_ref: registry://default
  tls_profile_ref: tls://registry-default
  mirror: true
```

---

### Step 7b: Kubernetes Manifest Emission

The placement decisions from Steps 1–6 are **orchestrator-agnostic** — only the
Step 7 rendering differs by target. To emit Kubernetes manifests instead of the
Swarm blueprint, run the companion script:

```bash
# native emitter — turns the blueprint's placements into k8s manifests
python scripts/emit_manifests.py --blueprint golden-deployment.yaml \
  --target kubernetes --out k8s/
```

Add a `target:` and `k8s:` block to the blueprint to drive it:

```yaml
target: kubernetes          # swarm | kubernetes
k8s:
  namespace: example-system
  nodeLabelKey: kubernetes.io/hostname
  storageClass: example-storage  # omit to use the cluster default
  ingressClass: example-ingress
```

**Native emitter mapping** (consumes the same `placements`, enriched from the
Step 2 catalog with `image`/`ports`/`volumes`/`mode`/`env`):

| Blueprint signal | Kubernetes output |
|---|---|
| placement `node` | `nodeAffinity` match on the configured `k8s.nodeLabelKey` |
| default placement | **Deployment** (`replicas` from catalog, default 1) |
| `volumes` present, or tier T2/T6 | **StatefulSet** + `volumeClaimTemplates` on `local-path` |
| `mode: global` | **DaemonSet** |
| `ports` published | **ClusterIP Service** (`published:target`) |
| every workload | placed in the blueprint `k8s.namespace` |

**Two emission paths:**

1. **Native** (above) — deterministic, no external tools; best for
   planner-owned catalog services. Matches the in-repo golden reference
   `agent-utilities/deploy/k8s/graphos.yaml`.
2. **kompose transform** — for the ~60 existing compose stacks, start from
   `kompose convert -f compose.yml -o k8s/`, then apply the deterministic
   post-fixups kompose drops:

   | Swarm/compose feature | kompose drops | Post-fixup |
   |---|---|---|
   | `deploy.placement.constraints` | dropped | inject `nodeAffinity` on `name=<host>` |
   | overlay networks (`caddy`, `internet`) | NetworkPolicy noise | replace with ClusterIP Service; cross-svc DNS `<svc>.<ns>.svc` |
   | named/bind volumes | hostPath/emptyDir | rewrite to `local-path` PVC pinned to the data's node |
   | `deploy.mode: global` | Deployment replicas:1 | convert to DaemonSet |
   | `depends_on` | dropped | initContainer wait + readiness probe |
   | host-mode ports (Caddy 80/443) | NodePort guess | `hostPort` on the edge node or `Service type: LoadBalancer` |

   For services that ship an upstream Helm chart (e.g. graph-os), prefer
   `helm upgrade --install` with a values file rendered from the placement.

The emitted `k8s/` dir is what the GitLab `k8s-deploy` CI job applies
(`kubectl apply -f k8s/`), and what the `portainer-agent` MCP can deploy as a
GitOps Kubernetes stack.

---

## Cross-Node Backup Pattern

For critical databases, implement cross-node backup replication:

```
PRIMARY DB (Node A) → BACKUP CRON (Node B with RAID)
```

**Pattern**: The backup service runs on a **different node** than the database it backs up, ensuring that a node failure doesn't destroy both the primary and the backup. Prefer nodes with RAID arrays (e.g., RAID10) for backup targets.

**Implementation:**
```yaml
# db-backup service constraint targets the BACKUP node (different from DB)
deploy:
  placement:
    constraints:
      - node.labels.name == BACKUP_NODE  # NOT the DB node
```

---

## Verification Checklist

After executing a deployment plan, verify:

1. **All services running**: `docker service ls | grep '0/' ` → should return empty
2. **No cross-node volume errors**: Check service logs for mount failures
3. **Network connectivity**: Each configured service URL returns its expected status
4. **Resource utilization**: No node exceeds 80% RAM or 90% CPU
5. **Registry accessibility**: All nodes can pull through the configured registry connection
6. **DNS resolution**: All overlay service names resolve within containers

## KG Schema (Optional)

When Graph-OS is available, persist the deployment topology:

| Node Type | Properties |
|---|---|
| `DeploymentPlan` | name, created_at, cluster_name |
| `ServicePlacement` | service_name, tier, target_node, reason |
| `MigrationTask` | service_name, source_node, target_node, migration_type, status |

| Edge Type | Connects |
|---|---|
| `PLACED_ON` | ServicePlacement → BladeServer |
| `PART_OF` | ServicePlacement → DeploymentPlan |
| `MIGRATES_FROM` | MigrationTask → BladeServer (source) |
| `MIGRATES_TO` | MigrationTask → BladeServer (target) |

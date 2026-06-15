---
name: ecosystem_bootstrap
description: >
  Self-deploying bootstrap workflow that unfolds the complete agent-utilities
  ecosystem on a fresh machine. Queries the user for deployment profile
  (homelab/enterprise/minimal), installs system dependencies via
  systems-manager-mcp, deploys core infrastructure (Docker, Portainer, Technitium DNS),
  service containers (wger, mealie, Jellyfin, etc.), and all MCP server
  containers as streamable-http Docker deployments. Transitions from
  container-manager-mcp to Portainer once deployed. Registers the full
  deployment topology in the Knowledge Graph.
domain: infrastructure
tags:
  - bootstrap
  - deployment
  - self-deploy
  - homelab
  - enterprise
  - docker
  - portainer
  - container-manager-mcp
  - systems-manager-mcp
  - graph-os
requires:
  - systems-manager-mcp
  - container-manager-mcp
  - portainer-mcp
  - technitium-dns-mcp
  - tunnel-manager-mcp
  - graph-os
---

# Ecosystem Bootstrap Workflow

Self-deploying bootstrap that unfolds agent-utilities and the full agent
ecosystem on a fresh machine or server. Walks through deployment profile
selection, prerequisite installation, core infrastructure, service containers,
MCP server containers, DNS routing, and Knowledge Graph registration.

## Steps

### Step 0: user-interaction

> **Canonical profiles** — agent-utilities' day-0 uses three tiers:
> **tiny** (all-local, zero-infra → `agent-utilities/scripts/bootstrap.sh`),
> **single-node-prod** (one durable host), and **enterprise** (full swarm). This
> workflow's `minimal`→**tiny/single-node-prod**, `homelab`/`enterprise`→**enterprise**.
> The `*-mcp` connector set per profile is the single source of truth in
> `agent-utilities/deploy/mcp-fleet.registry.yml` (see the
> `agent-os-genesis` / `day0` A-series steps).

Present the deployment profile questionnaire to the user. Ask:
1. **Deployment profile**: homelab (all services), enterprise (ITIL + productivity), or minimal (core infrastructure only)
2. **Target host**: localhost, remote SSH host (via tunnel-manager), or multi-node cluster
3. **DNS domain**: base domain for service routing (e.g., `home.lab`, `corp.example.com`)
4. **GPU availability**: whether to deploy GPU-accelerated services (data-science-mcp, CUDA models)
5. **External services**: which cloud services are already configured (Jira, ServiceNow, GitHub, etc.)
6. **Storage paths**: data volume mount points for persistent storage
Expected: deployment_profile, target_host, dns_domain, gpu_available, external_services, storage_config

### Step 1: systems-manager-mcp
Verify and install system prerequisites on the target host:
- Docker Engine + Docker Compose v2
- Python 3.11+ and pip/uv
- Git for repository cloning
- SSH server (if remote deployment via tunnel-manager)
- Network utilities (curl, wget, jq)
Use `systems_manager_execute` to run installation commands. Verify each dependency with version checks.
Expected: docker_version, python_version, git_version, system_ready
Depends On: Step 0

### Step 2: container-manager-mcp
Deploy **Tier 0: Core Infrastructure** containers directly via container-manager-mcp (Portainer isn't available yet):
- **Portainer CE** — container orchestration UI (port 9443)
- **Technitium DNS** — authoritative DNS server (port 5380/53)
- **Traefik** (optional) — reverse proxy for service routing
Use `container_manager_docker` with `action='docker_create_container'` for each. Create the shared Docker network `agent-net` first via `action='docker_create_network'`.
Expected: portainer_container_id, dns_container_id, agent_network_id
Depends On: Step 1

### Step 3: portainer-mcp
Verify Portainer is accessible and complete initial setup. Use `portainer_auth` to authenticate, then `portainer_environment` with `action='get_endpoints'` to confirm the local Docker endpoint is registered. All subsequent container deployments will use Portainer stacks.
Expected: portainer_auth_token, endpoint_id
Depends On: Step 2

### Step 4: technitium-dns-mcp
Configure Technitium DNS with DNS records for all services that will be deployed. Use `add_record` with `zone='arpa'` to create entries like:
- `portainer.{dns_domain}` → container IP
- `mealie.{dns_domain}` → container IP
- `wger.{dns_domain}` → container IP
- (one record per service in the selected deployment profile)
Expected: dns_records, record_count
Depends On: Step 2

### Step 5: portainer-mcp
Deploy **Tier 1: Platform Services** as Portainer stacks based on the deployment profile. Use `portainer_stack` with `action='create_standalone_stack'` for each stack. **Homelab profile** deploys all; enterprise/minimal deploy subsets:
- **Health**: wger (fitness), Mealie (meal planning)
- **Media**: Jellyfin (media server), qBittorrent (downloads)
- **Productivity**: Nextcloud (files/calendar), Listmonk (email)
- **Social**: Owncast (streaming), Postiz (social scheduling)
- **Observability**: Uptime Kuma (monitoring), Langfuse (LLM tracing), Grafana + Prometheus
- **Development**: Gitea/GitLab CE, SearXNG (search)
- **Enterprise** (if profile=enterprise): ServiceNow mid-server, LeanIX connector
Expected: deployed_stacks, stack_ids, service_urls
Depends On: Step 3, Step 4

### Step 6: portainer-mcp
Deploy **Tier 2: MCP Server Containers** as streamable-http Docker deployments. Each MCP server runs in its own container with health checks:
- `technitium-dns-mcp`, `container-manager-mcp`, `systems-manager-mcp`, `tunnel-manager-mcp`
- `portainer-mcp`, `uptime-kuma-mcp`, `mealie-mcp`, `wger-mcp`
- `qbittorrent-mcp`, `jellyfin-mcp`, `owncast-mcp`, `postiz-mcp`
- `langfuse-mcp`, `repository-manager-mcp`, `github-mcp`, `gitlab-mcp`
- `searxng-mcp`, `scholarx-mcp`, `nextcloud-mcp`, `home-assistant-mcp`
- `servicenow-mcp`, `leanix-mcp`, `atlassian-mcp`, `microsoft-mcp`
- `plane-mcp`, `listmonk-mcp`, `stirlingpdf-mcp`, `archivebox-mcp`
- `audio-transcriber-mcp`, `data-science-mcp`, `media-downloader-mcp`
- `arr-mcp`, `documentdb-mcp`, `vector-mcp`
Use `portainer_stack` with a docker-compose referencing each agent's `docker/Dockerfile`.
Expected: mcp_containers, mcp_endpoints, health_status
Depends On: Step 5

### Step 7: technitium-dns-mcp
Update DNS records with the actual container IPs for all deployed services and MCP servers. Use `add_record` for each MCP server endpoint.
Expected: mcp_dns_records, total_records
Depends On: Step 6

### Step 8: graph-os
Register the complete deployment topology in the Knowledge Graph. Use `graph_write` to create nodes:
- `DeploymentManifest` — the overall bootstrap record with profile, timestamp, host
- `DeploymentPhase` nodes for each tier (Tier 0, 1, 2)
- `MCPServerDeployment` nodes for each MCP server with endpoint URLs
- `PlatformService` nodes for each deployed service
- Create edges: `deployedOn`, `belongsToStack`, `resolvesDNSFor`, `dependsOn`, `bootstrappedBy`
Expected: manifest_node_id, topology_nodes, relationship_count
Depends On: Step 6, Step 7

### Step 9: user-interaction
Present the deployment summary dashboard to the user:
- Total services deployed (by tier)
- DNS routing table
- MCP server health status
- Knowledge Graph node count
- Service access URLs
- Next steps: run `full_infrastructure_discovery` to populate detailed container metrics
Expected: deployment_report, user_acknowledgment
Depends On: Step 8

---
name: ecosystem-bootstrap
skill_type: workflow
description: >
  Self-deploying bootstrap workflow that unfolds the complete agent-utilities
  ecosystem on a fresh machine. Resolves the canonical deployment profile
  (tiny/single-node-prod/enterprise), installs system dependencies via
  systems-manager-mcp, deploys core infrastructure (Docker, Portainer, Technitium DNS),
  service containers (wger, mealie, Jellyfin, etc.), and all MCP server
  containers as streamable-http Docker deployments. Transitions from
  container-manager-mcp to Portainer once deployed. Registers the full
  deployment topology in the Knowledge Graph.
domain: infrastructure-workflows
tags:
  - bootstrap
  - deployment
  - self-deploy
  - self-hosted
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
metadata:
  version: '1.2.1'
---

# Ecosystem Bootstrap Workflow

Self-deploying bootstrap that unfolds agent-utilities and the full agent
ecosystem on a fresh machine or server. Walks through deployment profile
selection, prerequisite installation, core infrastructure, service containers,
MCP server containers, DNS routing, and Knowledge Graph registration.

## Steps

### Step 0: select-deployment-profile [skill: user-interaction]

> **Canonical profiles** — agent-utilities day 0 uses three current tiers:
> **tiny** (all-local, zero-infra), **single-node-prod** (one durable host), and
> **enterprise** (multi-host Kubernetes). Do not translate legacy profile names.
> The `*-mcp` connector set per profile is the single source of truth in
> `agent-utilities/deploy/mcp-fleet.registry.yml`.

Present the deployment profile questionnaire to the user. Ask:
1. **Deployment profile**: tiny, single-node-prod, or enterprise
2. **Target host**: localhost, remote SSH host (via tunnel-manager), or multi-node cluster
3. **DNS profile reference**: AgentConfig connection/policy reference for service routing
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

### Step 3: verify-portainer [skill: portainer-mcp]
Verify Portainer is accessible and complete initial setup. Use `portainer_auth` to authenticate, then `portainer_environment` with `action='get_endpoints'` to confirm the local Docker endpoint is registered. All subsequent container deployments will use Portainer stacks.
Expected: portainer_auth_token, endpoint_id
Depends On: Step 2

### Step 4: configure-service-dns [skill: technitium-dns-mcp]
Configure DNS records through the AgentConfig-resolved DNS connection. Resolve the
zone from that profile and use `add_record` once per enabled service. Pass opaque
service and address references to the provider; do not retain resolved names or
addresses in workflow output.
Expected: dns_records, record_count
Depends On: Step 2

### Step 5: deploy-platform-services [skill: portainer-mcp]
Deploy **Tier 1: Platform Services** through the orchestrator selected by the
canonical deployment profile. Use the profile's enabled component set as the
source of truth; do not carry a separate environment-specific service list. Resolve
image, storage, identity, network, and TLS settings from each component profile.
Expected: deployed_stacks, stack_ids, service_urls
Depends On: Step 3, Step 4

### Step 6: deploy-mcp-services [skill: portainer-mcp]
Deploy the MCP connector set selected by the canonical fleet registry and deployment
profile. Each enabled connector receives a health check and only named AgentConfig
connection references; the workflow does not enumerate a local fleet. Use the
orchestrator adapter selected by the profile.
Expected: mcp_containers, mcp_endpoints, health_status
Depends On: Step 5

### Step 7: update-mcp-dns [skill: technitium-dns-mcp]
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

### Step 9: present-bootstrap-summary [skill: user-interaction]
Present the deployment summary dashboard to the user:
- Total services deployed (by tier)
- DNS routing table
- MCP server health status
- Knowledge Graph node count
- Service access URLs
- Next steps: run `full-infrastructure-discovery` to populate detailed container metrics
Expected: deployment_report, user_acknowledgment
Depends On: Step 8

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — select-deployment-profile; Step 1 — systems-manager-mcp; Step 2 — container-manager-mcp; Step 3 — verify-portainer; Step 4 — configure-service-dns; Step 5 — deploy-platform-services; Step 6 — deploy-mcp-services; Step 7 — update-mcp-dns; Step 8 — graph-os; Step 9 — present-bootstrap-summary

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

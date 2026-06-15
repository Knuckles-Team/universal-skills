---
name: service-deployment-orchestrator
description: Stateless parallel orchestrator workflow to deploy containerized swarm
  services with native Caddy routing, Keycloak OIDC SSO, Technitium DNS, GitLab GitOps
  seeding, Portainer deployment, Grafana observability, and Uptime Kuma monitoring.
domain: infra
tags:
- infra
- orchestrator
- provisioning
- swarm
- dns
- caddy
- sso
requires: []
---

# service-deployment-orchestrator Workflow

Stateless parallel orchestrator workflow to deploy containerized swarm services with native Caddy routing, Keycloak OIDC SSO, Technitium DNS, GitLab GitOps seeding, Portainer deployment, Grafana observability, and Uptime Kuma monitoring.

### Step 0: user-interaction
Gather user specifications for the new service, including naming, ports, DNS subdomains, auth (SSO/Keycloak), Portainer nodes, and observability preferences.
Expected: service_specifications

### Step 1: gitlab-repository-seeder [depends_on: Step 0]
Provision a Git repository on GitLab CE, configure CI/CD variables, and push standard boilerplate configurations (compose.yml, .gitlab-ci.yml, README.md, AGENTS.md).
Expected: git_repository_url

### Step 2: dns-record-manager [depends_on: Step 0]
Register zone records (A/CNAME) for the service subdomain in Technitium DNS pointing to the primary Caddy reverse-proxy host.
Expected: dns_record_status

### Step 3: caddy-route-manager [depends_on: Step 0]
Generate proxy route configuration blocks, append them to Caddyfile, and perform a hot reload of the Caddy service.
Expected: caddy_route_status

### Step 4: keycloak-client-onboarder [depends_on: Step 0]
Onboard the new service by creating and configuring an OIDC client within the homelab realm in Keycloak.
Expected: oidc_client_credentials

### Step 5: portainer-sync-agent [depends_on: Step 1, Step 2, Step 3, Step 4]
Deploy/update the Docker Swarm stack via Portainer utilizing the newly populated GitLab repository, linking it to the insecure local registry.
Expected: swarm_stack_status

### Step 6: service-observability-provisioner [depends_on: Step 5]
Integrate the container log path with Promtail, verify Prometheus is scraping service metrics, and execute an end-to-end service health sweep check.
Expected: service_health_report

### Step 7: uptime-kuma-sync [depends_on: Step 5]
Discover the Caddy front-end routing entry and provision a corresponding HTTP health monitor in the Uptime Kuma monitoring service.
Expected: uptime_kuma_sync_status

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — user-interaction
- **After level 0:** Step 1 — gitlab-repository-seeder; Step 2 — dns-record-manager; Step 3 — caddy-route-manager; Step 4 — keycloak-client-onboarder
- **After level 1:** Step 5 — portainer-sync-agent
- **After level 2:** Step 6 — service-observability-provisioner; Step 7 — uptime-kuma-sync

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

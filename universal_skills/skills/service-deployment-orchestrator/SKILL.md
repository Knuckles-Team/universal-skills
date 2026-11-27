---
name: service-deployment-orchestrator
skill_type: workflow
description: >-
  Deploy a containerized service through configured source-control, DNS, routing,
  OIDC, registry, orchestrator, observability, and health-monitor providers. Use
  when a new service must be provisioned end-to-end from AgentConfig profile
  references. Do not use for an ad hoc local container or raw endpoint setup.
domain: infrastructure-workflows
tags:
- infra
- orchestrator
- provisioning
- swarm
- dns
- caddy
- sso
requires:
  - caddy-mcp
  - keycloak-agent
  - portainer-agent
  - technitium-dns-mcp
  - uptime-kuma-agent
metadata:
  version: '1.7.0'
---

# service-deployment-orchestrator Workflow

Deploy a containerized service without embedding deployment topology. Every step
accepts named AgentConfig connection or policy references; provider URLs, realms,
namespaces, node identities, credentials, and local paths remain external.

### Step 0: user-interaction
Gather the service contract and named source-control, DNS, routing, identity,
registry, orchestrator, observability, and monitoring profile references. Reject
raw endpoints, credentials, hostnames, nodes, namespaces, and local paths.
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
Onboard the service through the configured OIDC provider and realm reference.
Expected: oidc_client_credentials

### Step 5: portainer-sync-agent [depends_on: Step 1, Step 2, Step 3, Step 4]
Deploy or update the stack through the configured orchestrator and verified
registry connection/trust profile. Never enable an insecure registry fallback.
Expected: swarm_stack_status

### Step 6: service-observability-provisioner [depends_on: Step 5]
Integrate the container log path with Promtail, verify Prometheus is scraping service metrics, and execute an end-to-end service health sweep check.
Expected: service_health_report

### Step 7: uptime-kuma-sync [depends_on: Step 5]
Discover the Caddy front-end routing entry and provision a corresponding HTTP health monitor in the Uptime Kuma monitoring service.
Expected: uptime_kuma_sync_status

## Steps

1. Gather the service contract and the named AgentConfig profile references (`profile_ref`) for source control, DNS, routing, identity, registry, orchestrator and monitoring. Verify that no raw endpoint, credential, hostname or local path appears in the request.
2. Run Step 0 to Step 4 in parallel with the skills `gitlab-repository-seeder`, `dns-record-manager`, `caddy-route-manager` and `keycloak-client-onboarder`. Verify that each returns its expected output (repository URL, DNS status, route status, OIDC client reference).
3. Deploy the stack with `portainer-sync-agent` after all four finish. Verify that the stack status reports the service running on the configured orchestrator and that no insecure registry fallback was used.
4. Wire observability and monitoring with `service-observability-provisioner` and `uptime-kuma-sync`. Verify that the health sweep passes and that an HTTP monitor exists for the Caddy route.
5. Offload the whole DAG with `graph_orchestrate action=execute_workflow` when arbora is reachable. Verify that the run trace shows every step finished with its expected output.

## Failure recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 5 is blocked | One of Steps 1-4 did not finish or failed | Fix the failing prerequisite step, rerun only it, and resume from Step 5 |
| Stack deploy fails on image pull | Registry trust or connection profile is wrong | Correct the registry profile reference, and never enable an insecure fallback |
| DNS name does not resolve after Step 2 | Record was created in the wrong zone or has not propagated | Re-run `dns-record-manager` with the correct zone profile and verify with `dig <service host>` |
| Uptime monitor reports down right after deploy | Caddy route or the service is not healthy yet | Check the route with `caddy-route-manager` and the stack status, and let the monitor recheck after both pass |

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — user-interaction
- **After level 0:** Step 1 — gitlab-repository-seeder; Step 2 — dns-record-manager; Step 3 — caddy-route-manager; Step 4 — keycloak-client-onboarder
- **After level 1:** Step 5 — portainer-sync-agent
- **After level 2:** Step 6 — service-observability-provisioner; Step 7 — uptime-kuma-sync

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

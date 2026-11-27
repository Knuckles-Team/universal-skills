---
name: mcp-service-secret-onboarding
skill_type: workflow
description: >-
  Onboard or rotate a fleet MCP service auth secret end to end: provision a Keycloak service-account client, store the secret in OpenBao, inject it into the Portainer stack and redeploy, then verify the served call. Use when an MCP service returns 401 on missing or stale admin credentials, when rotating a client secret, or when wiring a new service account. Do NOT use for human logins.
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: service-account onboarding and secret rotation for the MCP fleet
  execution_mode: sequential
  specialist_ids:
    - identity-agent
    - vault-agent
    - deployer-agent
  tool_assignments:
    identity-agent: [kc_realms, kc_clients, kc_users]
    vault-agent: [open_kv]
    deployer-agent: [pt_stack, pt_docker]
tags: ['keycloak', 'openbao', 'portainer', 'secret-rotation', 'service-account', 'mcp']
concept: CONCEPT:INFRA-002
requires:
  - keycloak-agent
  - openbao-mcp
  - portainer-agent
metadata:
  version: '1.7.0'
---

# MCP Service Secret Onboarding Workflow

Scope: Onboard or rotate a fleet MCP service's auth secret end-to-end: provision a Keycloak service-account client, store the secret in OpenBao, inject it into the service's Portainer stack (reconciling the drifted stored compose) and redeploy, then verify the served call works. Use when an MCP service 401s on missing/stale admin credentials, when rotating a client secret, or when wiring a new service-account into the fleet.

**CONCEPT:INFRA-002**

Deliver a service-account secret to a fleet MCP service end-to-end so the served process
authenticates instead of 401-ing: provision the Keycloak client, store the secret in the
vault, inject it into the Portainer stack, redeploy, and verify.

## Steps

1. Provision the service-account client with `kc_clients` and `kc_realms` (skill `keycloak-client-onboarder`). Verify that `client_secret` is returned and the client has `serviceAccountsEnabled=true`.
2. Write the credentials with `open_kv` to `apps/<service>` (skill `secret-vault-manager`). Verify that reading `apps/<service>` returns `client_id`, `client_secret` and `realm`.
3. Inject the env vars with `portainer_stack_env.py --compose-file <repo compose> --set-json` (skill `portainer-sync-agent`). Verify that the redeployed stack shows the `- VAR=${VAR}` lines in its stored compose.
4. Confirm the service with `pt_docker` (skill `analyze-portainer-health`). Verify that the service is 1/1 and a served call such as list-realms returns 200 before and after the token TTL.

### Step 0: Provision Identity [skill: keycloak-client-onboarder]
**Agent**: `identity-agent`
**Tools**: `kc_realms, kc_clients, kc_users`

Provision a confidential **service-account** client for the target service in the admin
realm (`serviceAccountsEnabled=true`, `standardFlowEnabled=false`) and grant its service
account the roles it needs (e.g. the master-realm `admin` role for an admin-API client).
Retrieve the generated `client_secret`.
Expected: `client_id, client_secret, realm`

### Step 1: Store Secret [skill: secret-vault-manager]
**Agent**: `vault-agent`
**Tools**: `open_kv`

Write the credentials to OpenBao (KV v2) at `apps/<service>` with fields
`client_id`/`client_secret`/`realm`. The vault is the durable source of truth; the stack
`.env` is a deploy-time mirror.
Expected: `vault_path`

### Step 2: Inject & Redeploy [skill: portainer-sync-agent]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, pt_docker`

Inject the credential env vars into the service's Portainer stack and redeploy using
`portainer-sync-agent`'s `portainer_stack_env.py` — **passing `--compose-file` with the
repo compose** so the stored (drifted) compose is reconciled and the `- VAR=${VAR}` lines
exist to inject the values. Feed the secret via `--set-json` so it never hits argv.
Expected: `redeploy_result`

### Step 3: Verify [skill: analyze_portainer_health]
**Agent**: `deployer-agent`
**Tools**: `pt_docker`

Confirm the service converged (1/1) and exec a served call that exercises the new
credential (e.g. a Keycloak admin list-realms) — it must return 200 before and after the
realm's short token TTL, proving the refresh path works.
Expected: `verification_result`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Service still returns 401 | Stored compose drifted and lacks the env lines | Re-run `portainer_stack_env.py` with `--compose-file` pointing at the repo compose and redeploy |
| Secret appears in process args | Secret passed on the command line | Rotate the secret in Keycloak and re-inject it via `--set-json` |
| Call works then fails after TTL | Service account lacks refresh path or role | Grant the needed role to the service account in `kc_users` and redeploy |

## Output
- Service authenticating with a self-refreshing service-account token (no more 401s)
- Secret stored in OpenBao (`apps/<service>`) and mirrored to the stack env
- Portainer stack reconciled with the repo compose and redeployed
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Each step depends on the previous one
(the secret flows provision → store → inject → verify), so run them sequentially:

- **Step 0** — Provision Identity (keycloak-client-onboarder)
- **then Step 1** — Store Secret (secret-vault-manager)
- **then Step 2** — Inject & Redeploy (portainer-sync-agent)
- **then Step 3** — Verify (analyze_portainer_health)

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

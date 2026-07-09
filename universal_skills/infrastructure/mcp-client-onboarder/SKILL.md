---
name: mcp-client-onboarder
domain: infrastructure
skill_type: skill
description: >-
  Onboard, scope, and revoke clients for the central MCP multiplexer. Creates a
  Keycloak client_credentials identity, generates an Eunomia authorization policy
  from a profile template (full-access / read-only / server-scoped / role-based),
  merges it into the multiplexer's zero-trust policy, and supports ephemeral
  (TTL) clients with an automatic reaper. Use when the user says "onboard an MCP
  client", "give an agent access to the multiplexer", "scope a client to servers
  X,Y", "create a read-only MCP client", "revoke/expire an MCP client", or
  "mcp access control". Do NOT use for remote per-service Eunomia policies
  (use eunomia-policy-manager) or general Keycloak SSO (use the Keycloak skill).
license: MIT
tags: [mcp, multiplexer, authorization, eunomia, keycloak, zero-trust, onboarding, security]
metadata:
  version: '1.1.0'
  author: Genius
---

# MCP Client Onboarder

One-shot onboarding for the **central MCP multiplexer** (`mcp-multiplexer.arpa`).
The multiplexer is zero-trust: every request carries a verified Keycloak JWT, and
**Eunomia** authorizes each principal (the token's `azp`/`client_id` →
`agent:<id>`). This skill provisions both halves of a new client — identity
(Keycloak) and authorization (an Eunomia rule) — and can expire them.

## Access-control model (resolution order)

The multiplexer evaluates an **embedded** Eunomia policy file
(`services/mcp-multiplexer/eunomia_policy.json`) in this order:

1. **`default_effect: deny`** — nothing is allowed unless a rule says so.
2. **`_base-meta-tools`** (inherited by every authenticated principal) — grants
   only the gateway's own discovery/control meta-tools (`find_tools`,
   `list_catalog`, `load_tools`, `unload_tools`, `multiplexer_status`) so a scoped
   client can still find and load what it IS allowed to execute.
3. **Per-client rules** (added by this skill) — grant actual capability.

Two independent layers gate a tool, and **both** must allow it: Eunomia
(principal — this skill) and the per-session visibility middleware (has *this
session* `load_tools`-ed it — plan Phase 5). The principal is bound to the
cryptographically verified JWT, not a spoofable header.

## Profiles

| Profile | Grants | Flags |
|---|---|---|
| `full-access` | list + execute every tool | — |
| `read-only` | discover (list) everything, execute nothing (real tools) | — |
| `server-scoped` | list + execute only the named servers' tools | `--servers a,b` |
| `role-based` | the servers mapped to a role in `templates/roles.json` | `--role devops` |

## Onboard

```bash
export KEYCLOAK_ADMIN_PASSWORD=…            # to create the Keycloak client

# full access
python scripts/onboard.py my-agent --profile full-access

# read-only auditor
python scripts/onboard.py auditor --profile read-only

# scoped to two servers, expires in 24h (ephemeral)
python scripts/onboard.py ci-bot --profile server-scoped \
    --servers github-mcp,gitlab-mcp --ttl 24h

# a named role
python scripts/onboard.py oncall --profile role-based --role devops
```

Onboarding is **idempotent** (re-running replaces the client's prior rules) and
prints the client secret (store it in **OpenBao** — never commit). It writes the
policy file but does **not** restart the service: **restart the mcp-multiplexer**
afterwards so the embedded PDP reloads the policy (it is read at boot). The client
then mints tokens with `services/mcp-multiplexer/mint_token.py` and connects with
`Authorization: Bearer <token>`.

## Ephemeral clients + reaper

`--ttl` records an expiry in `ephemeral_clients.json` (Eunomia has no native TTL).
The reaper revokes anything past expiry — removing its policy rules **and** its
Keycloak client:

```bash
python scripts/reap.py --dry-run                 # report what would be revoked
KEYCLOAK_ADMIN_PASSWORD=… python scripts/reap.py # revoke expired
```

Schedule it hourly (cron or a daemon tick). Restart the multiplexer after a
revocation.

## Revoke explicitly

```bash
python -c "from scripts.policy_rules import remove_client_rules; \
  from pathlib import Path; \
  print(remove_client_rules(Path('/home/apps/workspace/services/mcp-multiplexer/eunomia_policy.json'),'ci-bot'))"
KEYCLOAK_ADMIN_PASSWORD=… python -c "import scripts.keycloak_client as k; k.delete_client('ci-bot', k.get_admin_token())"
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `KEYCLOAK_URL` | `http://keycloak.arpa` | Keycloak base URL |
| `KEYCLOAK_REALM` | `homelab` | realm holding the machine clients |
| `KEYCLOAK_ADMIN_PASSWORD` | — | admin password (required for client create/delete) |
| `MCP_POLICY_FILE` | `…/services/mcp-multiplexer/eunomia_policy.json` | the embedded policy file |
| `MCP_EPHEMERAL_FILE` | `…/services/mcp-multiplexer/ephemeral_clients.json` | TTL sidecar |

## Files

- `scripts/onboard.py` — one-shot onboarding (Keycloak client + policy rule + TTL).
- `scripts/reap.py` — revoke expired ephemeral clients.
- `scripts/policy_rules.py` — profile → Eunomia rule generation + idempotent policy merge.
- `scripts/keycloak_client.py` — minimal `client_credentials` provisioning (urllib only).
- `templates/` — reference rule shapes + `roles.json`.

## References
- [agent-os-deployment](../agent-os-deployment/SKILL.md) — day-0 multiplexer setup (steps 2/2b).
- [eunomia-policy-manager](../eunomia-policy-manager/SKILL.md) — remote per-service policies (different target).

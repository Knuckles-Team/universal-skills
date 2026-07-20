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
  version: '1.2.1'
  author: Genius
---

# MCP Client Onboarder

One-shot onboarding for the configured **central MCP multiplexer**.
The multiplexer is zero-trust: every request carries a verified Keycloak JWT, and
**Eunomia** authorizes each principal (the token's `azp`/`client_id` →
`agent:<id>`). This skill provisions both halves of a new client — identity
(Keycloak) and authorization (an Eunomia rule) — and can expire them.

## Access-control model (resolution order)

The multiplexer evaluates its configured **embedded** Eunomia policy file in this
order:

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

Onboarding is **idempotent** (re-running replaces the client's prior rules). It
never prints or stores the client secret; retrieve that credential through the
identity provider's approved secret-management workflow. It writes the policy
file but does **not** restart the service: restart the configured multiplexer so
the embedded PDP reloads the policy. Clients connect with an
`Authorization: Bearer <token>` header obtained outside this skill.

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
  print(remove_client_rules(Path('${MCP_POLICY_FILE}'),'ci-bot'))"
KEYCLOAK_ADMIN_PASSWORD=… python -c "import scripts.keycloak_client as k; k.delete_client('ci-bot', k.get_admin_token())"
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `KEYCLOAK_URL` | required | HTTPS Keycloak base URL (plain HTTP is loopback-only) |
| `KEYCLOAK_REALM` | `master` | realm holding the machine clients |
| `KEYCLOAK_ADMIN_REALM` | `master` | realm used to obtain the administrator token |
| `KEYCLOAK_ADMIN_PASSWORD` | — | admin password (required for client create/delete) |
| `MCP_POLICY_FILE` | XDG config | the embedded policy file |
| `MCP_EPHEMERAL_FILE` | XDG config | owner-only TTL sidecar |

TLS verification is mandatory. Configure a complete runtime trust chain with
`SSL_CERT_FILE`, `SSL_CERT_DIR`, or `REQUESTS_CA_BUNDLE`; paths and certificate
contents are read only at runtime and are never copied into reports or traces.

## Files

- `scripts/onboard.py` — one-shot onboarding (Keycloak client + policy rule + TTL).
- `scripts/reap.py` — revoke expired ephemeral clients.
- `scripts/policy_rules.py` — profile → Eunomia rule generation + idempotent policy merge.
- `scripts/keycloak_client.py` — minimal `client_credentials` provisioning (urllib only).
- `templates/` — reference rule shapes + `roles.json`.

## References
- `agent-os-deployment` — package-owned day-0 multiplexer setup; use it only when
  its owning agent package is installed.
- [eunomia-policy-manager](../eunomia-policy-manager/SKILL.md) — remote per-service policies (different target).

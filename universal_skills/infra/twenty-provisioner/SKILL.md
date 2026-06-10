---
name: twenty-provisioner
description: >
  Twenty CRM day-0 provisioning atomic skill. Headlessly bootstraps a Twenty workspace
  admin account, mints a long-lived API key via Twenty's /metadata GraphQL, stores it in
  OpenBao + the service .env, wires twenty-mcp + egeria-mcp, and (best-effort) configures
  Keycloak OIDC SSO. Reproducible for a day-0 / fresh install.
domain: infrastructure
tags:
  - twenty
  - crm
  - provisioning
  - api-key
  - oidc
  - sso
  - day0
requires:
  - openbao-mcp        # store the credential (optional but recommended)
  - keycloak-mcp       # SSO client (optional)
---

# Twenty Provisioner Skill

Headless, reproducible provisioning of a Twenty CRM instance: **admin account → API key →
secret storage → MCP wiring → SSO**. Built from a verified live run (2026-06-10,
`twentycrm/twenty:latest`).

## ⚑ The one thing to know: Twenty's auth API is at `/metadata`

Twenty exposes **two** GraphQL schemas:
- `POST /graphql` — the per-workspace **object** schema only (companies/people CRUD).
- `POST /metadata` — the **core/auth/system** schema: `signUp`, `getLoginTokenFromCredentials`,
  `getAuthTokensFromLoginToken`, `getRoles`, `createApiKey`, `generateApiKeyToken`,
  `createOIDCIdentityProvider`, `currentWorkspace`, etc.

Every auth/admin/api-key call goes to `/metadata`, with an `Origin: <base-url>` header
(Twenty resolves the workspace from it). GraphQL **introspection is disabled** — discover
schema via the Metadata REST API instead (`/rest/metadata/objects|fields|relations`).

## Prerequisites (day-0)

1. **Twenty stack deployed** (Portainer/GitOps). Compose must set `ACCESS_TOKEN_SECRET`,
   `REFRESH_TOKEN_SECRET`, `ENCRYPTION_KEY`, `PG_DATABASE_URL`, `REDIS_URL`, `SERVER_URL`,
   `FRONTEND_URL`. For SSO also: `AUTH_SSO_ENABLED=true`, `AUTH_OIDC_ENABLED=true`,
   `AUTH_OIDC_ISSUER`, `AUTH_OIDC_CLIENT_ID`, `AUTH_OIDC_CLIENT_SECRET`,
   `AUTH_OIDC_CALLBACK_URL=<url>/auth/oidc/callback`. Service is healthy when
   `curl <url>/healthz` returns `{"status":"ok"}`.
2. **Keycloak realm + OIDC client** for Twenty (use the `keycloak-client-onboarder` skill):
   client_id `twenty`, redirect URIs `<url>/*`, a client secret. Realm OIDC discovery at
   `<kc>/realms/<realm>/.well-known/openid-configuration` must return 200.
3. **OpenBao unsealed** (use `secret-vault-manager`) if storing the credential there.

## Step 1 — Bootstrap the admin account (first user + workspace)

Either drive the UI signup with the `agent-browser` skill (headless: see that skill's
`bootstrap.sh --connect` — internal `*.arpa` http needs Chromium's HTTPS-Upgrade disabled),
**or** headlessly via the `signUp` mutation on `/metadata` (set `SIGNUP=1` below). New
workspaces still need onboarding (`/create/workspace` → name → profile → finish) before the
account is fully usable; the UI path completes this automatically.

## Step 2 — Mint a long-lived API key (the core primitive)

Run the bundled script (verified end-to-end):

```bash
TWENTY_URL=http://twenty.arpa \
TWENTY_EMAIL=admin@homelab.arpa TWENTY_PASSWORD='<password>' \
KEY_NAME=egeria-harvester \
bash provision_twenty.sh        # prints the API key to stdout (capture once)
```

It performs, all on `/metadata`:
`getLoginTokenFromCredentials(email,password,origin)` → `getAuthTokensFromLoginToken(loginToken,origin)`
→ `getRoles` (pick `canUpdateAllSettings`=Admin) → `createApiKey(input:{name,expiresAt,roleId})`
→ `generateApiKeyToken(apiKeyId:UUID!,expiresAt:String!)`, then validates against
`/rest/companies` (expects HTTP 200). **Gotchas baked in:** `roleId` is required on
`createApiKey`; `generateApiKeyToken` mixes `apiKeyId:UUID!` + `expiresAt:String!`.

Equivalent via `twenty-mcp` (once installed): the `twenty_provision_api_key` MCP tool, or
`twenty_gql.GraphQL(url, ...).provision_api_key(email, password)`.

## Step 3 — Persist the credential

```bash
# service .env (source of truth for the stack repo)
printf 'TWENTY_TOKEN=%s\n' "$API_KEY" >> ~/workspace/services/twenty/.env
# OpenBao (KV v2 mount 'apps')
curl -s -X POST -H "X-Vault-Token: $BAO_ROOT_TOKEN" -H 'Content-Type: application/json' \
  "$OPENBAO_URL/v1/apps/data/homelab/twenty" \
  --data "{\"data\":{\"url\":\"$TWENTY_URL\",\"login_email\":\"$TWENTY_EMAIL\",\"login_password\":\"$TWENTY_PASSWORD\",\"api_token\":\"$API_KEY\"}}"
```

## Step 4 — Wire the MCP servers (`mcp_config.json`)

- `twenty-mcp` env: `"disabled": false`, `TWENTY_URL=<url>`, `TWENTY_TOKEN=<api key>`.
- `egeria-mcp` env: add `TWENTY_URL=<url>`, `TWENTY_TOKEN=<api key>`, and
  `EGERIA_ENABLE_WRITE=true` (gates all harvest/write tools). Restart the MCP multiplexer.

## Step 5 — Verify

- `curl -H "Authorization: Bearer $API_KEY" "<url>/rest/companies?limit=1"` → 200 + data.
- Egeria harvest: `eg__harvest_crm` (or `eg__harvest layer=crm`) → report with
  `summary.records>0`, no `skipped`. Confirm assets via `eg__asset_search Twenty`:
  `DataStore::twenty` (SoftwareServer) + `Dataset::Twenty::{Company,Person}::*`
  (`additionalProperties.source=Twenty`, confidentiality L2/L3).

## Step 6 — Keycloak OIDC SSO (best-effort; see KNOWN ISSUE)

Intended (authenticated, on `/metadata`):
```graphql
mutation { createOIDCIdentityProvider(input:{
  name:"Keycloak", issuer:"<kc>/realms/<realm>",
  clientID:"twenty", clientSecret:"<kc client secret>"
}){ id type name issuer status } }
```
Get the KC client secret from `GET <kc>/admin/realms/<realm>/clients/<uuid>/client-secret`.

> **KNOWN ISSUE (twentycrm/twenty:latest, 2026-06-10):** both `getSSOIdentityProviders`
> (query) and `createOIDCIdentityProvider` (mutation) fail **server-side** with
> `Cannot read properties of undefined (reading 'headers')` regardless of input/token,
> while every other `/metadata` op works. SSO-IdP provisioning via the API is therefore
> blocked on this build. Workarounds: pin Twenty to a version where SSO management works;
> create the IdP via Settings→Security→SSO in the UI; or rely on the env-based global
> `AUTH_OIDC_*` (note: on this build the login UI still showed only email/password —
> the harvester does **not** need SSO; it uses the API key).

## Notes
- API keys are **role-scoped** (Twenty ≥ recent) — always pass `roleId`.
- Access tokens from the login flow are short-lived and also work as `Bearer` on `/rest`;
  the **API key** is the durable credential for automation/harvesters.
- The harvester (`egeria-mcp` `harvest_crm`) reads `/rest/companies` + `/rest/people` with
  the Bearer key and catalogs them into Egeria.

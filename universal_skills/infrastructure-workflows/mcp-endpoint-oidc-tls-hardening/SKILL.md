---
name: mcp-endpoint-oidc-tls-hardening
skill_type: workflow
description: >-
  Harden a fleet MCP endpoint's INBOUND listener with OIDC bearer-token
  validation plus TLS, via keycloak-mcp + openbao-mcp + k8s tools only — no
  manual Keycloak console. Reuse-first: checks if the existing `homelab`
  realm/client (aud `agent-services`) already covers the endpoint before
  minting anything new; only then provisions a client, stores the secret in
  OpenBao, sets AUTH_JWT_ISSUER/JWKS_URI/AUDIENCE + MCP_AUTH_TYPE=jwt, issues a
  cert-manager cert with a zero-disruption `tls:` ingress patch, repoints the
  client, and verifies. Use for "secure/harden an MCP endpoint", "add OIDC
  auth", "put TLS on an internal endpoint", "require a bearer token". Do NOT
  use for a service's own outbound creds to another admin API (use
  mcp-service-secret-onboarding) or rotating an already-hardened endpoint's
  secret (use automated-credential-rotation).
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: harden an MCP endpoint's inbound OIDC bearer auth + TLS transport
  execution_mode: sequential
  specialist_ids:
    - identity-agent
    - vault-agent
    - tls-agent
    - deployer-agent
    - verify-agent
  tool_assignments:
    identity-agent: [keyc__get_realm, keyc__get_client, keyc__create_client, keyc__regenerate_client_secret_by_client_id, keyc__delete_client]
    vault-agent: [open__read_secret, open__write_secret, open__delete_secret]
    tls-agent: [cnt_cm_k8s_config, tun_tm_remote]
    deployer-agent: [cnt_cm_k8s_config, cnt_cm_k8s_networking]
    verify-agent: [tun_tm_remote, graph_write]
tags: [keycloak, openbao, oidc, jwt, tls, cert-manager, mcp, hardening, bearer-auth, ingress]
concept: CONCEPT:INFRA-001
requires:
  - keycloak-agent
  - openbao-mcp
  - container-manager-mcp
metadata:
  version: '1.2.0'
---

# MCP Endpoint OIDC + TLS Hardening Workflow

**CONCEPT:INFRA-001**

Turn any fleet MCP endpoint from open/unauthenticated (or HTTP-only) into one that
validates a homelab-issued OIDC bearer token and serves over TLS — driven entirely
through `keycloak-mcp` and `openbao-mcp` (+ the k8s fleet tools for the
resource-server env and ingress), with **no manual Keycloak console work**. This is
the repeatable version of the live recipe used to harden graph-os's endpoint.

## Reuse-first principle — read before Step 0

**Most endpoints need zero new Keycloak objects.** The homelab realm already has a
`mcp-multiplexer` client (`aud: agent-services`), and the fleet's JWT-validating
resource servers (e.g. graph-os) already trust it via:

```
AUTH_JWT_ISSUER=http://keycloak.arpa/realms/homelab
AUTH_JWT_JWKS_URI=http://keycloak.platform.svc:8080/realms/homelab/protocol/openid-connect/certs
AUTH_JWT_AUDIENCE=agent-services
MCP_AUTH_TYPE=jwt
```

If the endpoint you're hardening can accept tokens from that same realm/audience,
**Step 1 (provision a new client) is skipped entirely** — you only need Step 3
(point the endpoint's own resource-server env at the existing issuer/JWKS/audience)
and Step 4 (TLS). Only mint a **new** dedicated client when the endpoint genuinely
needs its own service-account identity (distinct authorization scope, separate
audit trail, or a different audience). Deciding this correctly is Step 0 — don't
skip it to "be safe"; an unnecessary new client is exactly the sprawl this workflow
exists to prevent.

## Steps

### Step 0: assess_reuse
**Agent**: `identity-agent`
**Tools**: `keyc__get_realm, keyc__get_client, open__read_secret`

Confirm the target realm (`keyc__get_realm(realm="homelab")`) and check whether an
existing client already covers this endpoint's audience — read the existing
`mcp-multiplexer` credentials for shape/reference:
`open__read_secret(mount="apps", path="mcp-multiplexer")`, and
`keyc__get_client(realm="homelab", client_id="mcp-multiplexer")` to confirm its
`agent-services` audience mapper. Decide: **reuse** (no new client — go straight to
Step 3) or **new-client-needed** (proceed to Step 1). Record the rationale either way.
Expected: `reuse_decision, rationale, existing_client_reference`

### Step 1: provision_client [depends_on: assess_reuse — only if reuse_decision=false]
**Agent**: `identity-agent`
**Tools**: `keyc__create_client, keyc__regenerate_client_secret_by_client_id`

Create a confidential, service-account client scoped to this endpoint:

```
keyc__create_client(
  realm="homelab",
  client_id="<svc>",
  client_representation={
    "clientId": "<svc>",
    "serviceAccountsEnabled": true,
    "publicClient": false,
    "standardFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "clientAuthenticatorType": "client-secret",
  },
)
keyc__regenerate_client_secret_by_client_id(realm="homelab", client_id="<svc>")
  -> {value, client_uuid}
```

Add (or confirm) an **audience mapper** on the new client so its tokens carry
`aud` including the resource server's expected audience (`agent-services`, unless
the endpoint intentionally uses a distinct audience — in which case Step 3 must
match it exactly). **Rollback**: `keyc__delete_client(realm="homelab",
client_uuid=<uuid>)`.
Expected: `client_id, client_uuid, client_secret`

### Step 2: store_secret [depends_on: provision_client]
**Agent**: `vault-agent`
**Tools**: `open__write_secret`

Write the credentials to OpenBao as the durable source of truth — **never** into a
committed file or chat transcript:

```
open__write_secret(
  mount="apps", path="<svc>",
  secret_data={
    "OIDC_CLIENT_ID": "<svc>",
    "OIDC_CLIENT_SECRET": "<value>",
    "OIDC_ISSUER": "http://keycloak.arpa/realms/homelab",
    "OIDC_JWKS_URI": "http://keycloak.platform.svc:8080/realms/homelab/protocol/openid-connect/certs",
    "OIDC_TOKEN_URL": "http://keycloak.arpa/realms/homelab/protocol/openid-connect/token",
    "OIDC_AUDIENCE": "agent-services",
  },
)
```
**Rollback**: `open__delete_secret(mount="apps", path="<svc>")` if the run aborts
before the resource server is reconfigured.
Expected: `vault_path`

### Step 3: configure_resource_server [depends_on: store_secret, or directly after assess_reuse if reuse_decision=true]
**Agent**: `deployer-agent`
**Tools**: `cnt_cm_k8s_config`

Point the endpoint's own deployment at the issuer it should trust — reused or new,
the shape is identical (this is the same env graph-os already runs on):

```
AUTH_JWT_ISSUER=http://keycloak.arpa/realms/homelab
AUTH_JWT_JWKS_URI=http://keycloak.platform.svc:8080/realms/homelab/protocol/openid-connect/certs
AUTH_JWT_AUDIENCE=agent-services   # or the new client's audience if it diverges
MCP_AUTH_TYPE=jwt
```

Apply via `cnt_cm_k8s_config action=patch_resource resource_type=configmap
name=<endpoint>-env namespace=<ns> patch_body={...}` (or `create_configmap` if the
endpoint has no env configMap yet), then roll the deployment so the new env takes
effect. Do not enable bearer-auth enforcement until Step 6 confirms a good token
is accepted — a bad env value here locks out every caller.
Expected: `resource_server_env_applied`

### Step 4: provision_tls [depends_on: configure_resource_server]
**Agent**: `tls-agent`
**Tools**: `cnt_cm_k8s_config, tun_tm_remote`

Add HTTPS **alongside** the existing HTTP listener — zero-disruption, additive:

1. Issue a `Certificate` for `<host>.arpa` off the already-provisioned internal-CA
   `ClusterIssuer` (`homelab-arpa-ca`) — apply the manifest via `tun_tm_remote`
   (`kubectl apply -f -`) or `cnt_cm_k8s_config action=list_custom_resources` /
   equivalent CRD tooling if the endpoint's namespace already has one to clone.
2. Patch the ingress with a `tls:` block referencing the new cert secret, keeping
   `nginx.ingress.kubernetes.io/ssl-redirect: "false"` so HTTP keeps serving
   unchanged — callers migrate to HTTPS on their own schedule, nothing breaks mid-run:
   `cnt_cm_k8s_config action=patch_resource resource_type=ingress
   name=<endpoint> namespace=<ns> patch_body={...tls block + annotation...}`.
3. Extract the CA for client trust distribution:
   `kubectl -n cert-manager get secret homelab-arpa-ca-secret -o
   jsonpath='{.data.tls\.crt}' | base64 -d` (via `tun_tm_remote`).
Expected: `certificate_issued, ingress_patched, ca_bundle`

### Step 5: repoint_client [depends_on: provision_tls]
**Agent**: `deployer-agent`

Point the MCP client configuration at `https://<host>.arpa/mcp`, presenting a
homelab bearer token minted with `grant_type=client_credentials` against
`http://keycloak.arpa/realms/homelab/protocol/openid-connect/token` using the
`OIDC_CLIENT_ID`/`OIDC_CLIENT_SECRET` from Step 2 (or the reused client's creds).
**Token-refresh note**: client-credentials tokens expire — prefer the client's
built-in OAuth/token-refresh support over caching a static `Authorization` header,
or the endpoint will start 401-ing mid-session once the token lapses.
Expected: `client_repointed`

### Step 6: verify [depends_on: repoint_client]
**Agent**: `verify-agent`
**Tools**: `tun_tm_remote, graph_write`

Mint a token and decode it: confirm `iss` matches `OIDC_ISSUER`, `aud` includes
`OIDC_AUDIENCE`, and `azp` is the expected client. Confirm the endpoint accepts a
call with the token (200) and **rejects** a call with no token or a token bearing
the wrong `aud` (401) — a hardening run that only tests the happy path hasn't
verified the auth is actually enforced. Confirm the HTTPS listener validates
against the CA extracted in Step 4 (no cert warning) and that HTTP still serves
(zero-disruption check). Persist the whole run — client id (never the secret),
vault path, cert details, verification results — as provenance via `graph_write`.
Expected: `verification_result, provenance_ref`

## Output
- Endpoint validates homelab-issued OIDC bearer tokens (`MCP_AUTH_TYPE=jwt`,
  correct issuer/JWKS/audience) and rejects unauthenticated/wrong-audience calls.
- Endpoint serves HTTPS via a cert-manager-issued internal-CA cert alongside its
  existing HTTP listener (no downtime, `ssl-redirect` off until callers migrate).
- Credentials (if a new client was provisioned) live only in OpenBao
  (`apps/<svc>`) — never echoed into a file or transcript.
- Audit trail in the KG: client id, vault path, cert secret name, verification
  outcome, timestamps.

## Safety invariants
- **Reuse-first, always.** Step 0 is not optional — never provision a new
  Keycloak client when the existing `homelab` realm / `mcp-multiplexer` audience
  already covers the endpoint.
- **Never echo `OIDC_CLIENT_SECRET`** (or any vault-read value) into a committed
  file, log, or chat transcript. Route secret material through OpenBao only.
- **TLS is additive, not a cutover.** Never remove or disable the HTTP listener in
  the same run that adds HTTPS — `ssl-redirect: "false"` keeps both paths live
  until the operator deliberately flips it.
- **Don't enforce auth before verifying it.** Confirm a good token is accepted
  (Step 6) before treating the endpoint as hardened; a misconfigured
  issuer/JWKS/audience locks out every legitimate caller with no rollback path
  except reverting the configMap.

## Rollback
- **New client provisioned (Step 1) but the run aborts before Step 3**: delete it —
  `keyc__delete_client(realm="homelab", client_uuid=<uuid>)`.
- **Secret written (Step 2) but the run aborts**: `open__delete_secret(mount="apps",
  path="<svc>")`.
- **Resource-server env applied (Step 3) but verification (Step 6) fails**: revert
  the configMap patch (previous values) and roll the deployment back; the endpoint
  returns to its prior (unauthenticated or previously-configured) state.
- **TLS (Step 4)**: delete the `Certificate` object and revert the ingress `tls:`
  patch — HTTP was never touched, so this is a clean no-op rollback.

## Related
- **`keycloak-client-onboarder`** — the atomic client-provisioning primitive Step 1
  wraps; invoked only when Step 0 decides reuse isn't possible.
- **`mcp-service-secret-onboarding`** — the *outbound* counterpart: gives an MCP
  service its own service-account credentials to call *another* admin API. This
  workflow instead hardens the endpoint's *inbound* listener (bearer validation +
  transport). Use both together when a service needs to both authenticate itself
  outbound and require auth inbound.
- **`automated-credential-rotation`** — rotates the OIDC client secret this
  workflow provisions, on the standard 6-month cadence, once the endpoint is
  hardened.
- **`ca-trust-provisioner`** — if downstream clients need the internal CA folded
  into their OS trust store (not just handed the PEM), run this after Step 4.

## Execution

Run this workflow as a dependency-ordered chain: Steps 0-3 are strictly
sequential (each depends on the identity/secret state the previous step
produced); once the resource server trusts the issuer, TLS (Step 4) can be
provisioned in parallel with any remaining Step 3 rollout, then Steps 5-6 close
the loop.

- **Run first:** Step 0 — assess_reuse
- **After Step 0 (only if a new client is needed):** Step 1 — provision_client,
  **then** Step 2 — store_secret
- **After Step 2 (or directly after Step 0 if reusing):** Step 3 —
  configure_resource_server
- **Can run in parallel with Step 3's rollout:** Step 4 — provision_tls
- **After Step 3 and Step 4:** Step 5 — repoint_client
- **After Step 5:** Step 6 — verify

**Execution:** If graph-os is reachable, offload the whole DAG via
`graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true
parallel/swarm execution. Otherwise execute the steps natively in dependency
order: run steps with no unmet `depends_on` in parallel, then their dependents.

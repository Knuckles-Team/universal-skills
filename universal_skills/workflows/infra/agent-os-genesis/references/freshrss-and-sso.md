# FreshRSS world-model intake + Caddy/Keycloak SSO — genesis standard

How genesis stands up the **FreshRSS** world-model RSS source (the `freshrss-agent`
connector + the FreshRSS app) and the **reusable Caddy + Keycloak OIDC SSO** layer
(`caddy-security`) that protects `*.arpa` web apps. Validated live 2026-06-18.

Two independent surfaces — keep them separate:
- **Ingestion / API path** (`freshrss.arpa/api/greader.php`) — token auth (GReader
  `GoogleLogin`), driven by the `freshrss-mcp` connector. **Never** behind the SSO portal.
- **Web UI** (`freshrss.arpa/…`) — Keycloak SSO via `caddy-security` + FreshRSS `http_auth`.

---

## 1. FreshRSS app configuration (on its placement node)

FreshRSS ships uninstalled. Install + enable the API via the in-container CLI:

```bash
cid=$(docker ps --filter name=freshrss -q | head -1)
docker exec -e TZ=America/Chicago $cid php cli/do-install.php \
  --default-user admin --base-url http://freshrss.arpa --language en \
  --auth-type form --api-enabled --db-type sqlite
docker exec -e TZ=America/Chicago $cid php cli/create-user.php \
  --user admin --password "<LOGIN_PW>" --api-password "<API_PW>" --language en
# CRITICAL: the CLI writes config as root; the web user (www-data) can't read it →
# GReader ClientLogin returns "configuration cannot be found". Re-apply perms:
docker exec $cid ./cli/access-permissions.sh
```

Verify the API: `curl "http://freshrss.arpa/api/greader.php/accounts/ClientLogin?Email=admin&Passwd=<API_PW>"` → `SID=…/Auth=…` (not 503/Unauthorized).

**Secrets** → OpenBao `apps/freshrss-mcp` (openbao-mcp `open__kv kv2_put`, params
`mount_path`/`secret_path`/`data`): `FRESHRSS_URL`, `FRESHRSS_USER`,
`FRESHRSS_API_PASSWORD`, `FRESHRSS_SSL_VERIFY`. Mirror into `services/freshrss-mcp/.env`.

**Curated feeds** (the world-model categories + ScholarX arXiv unification) via the
`freshrss_subscriptions` MCP tool or `reports/freshrss/seed_feeds.py` over
`curated_feeds.json` (Markets & Finance · Tech/AI/Cyber · Macro/Geopolitics ·
Science+Breaking · **Research (ScholarX)** = arXiv cs.AI/LG/CL/MA/CR + stat.ML).

## 2. freshrss-mcp connector deploy (editable, no publish)

`services/freshrss-mcp/compose.dev.yml` — source-mount `/au`+`/src`, `PYTHONPATH=/au:/src`,
image built **locally** from `agents/freshrss-agent/docker/debug.Dockerfile` (the prod
Dockerfile pip-installs from PyPI; debug builds from local source). Registered in
`agent-utilities/deploy/mcp-fleet.registry.yml` (host_port 8254) and
`mcp_config*.json` + `services/mcp-multiplexer/mcp_config_central.json`. The KG side
(`MCP_TOOL_PRESETS["freshrss"]` + `_sync_freshrss` + `WorldModelPipelineRunner`) is in
agent-utilities; the source connector authenticates outbound to the JWT-protected
`freshrss-mcp` via the service-account bearer (`MCP_CLIENT_AUTH`, OS-5.32).

---

## 3. Caddy + Keycloak OIDC SSO standard (`caddy-security`)

The reusable pattern for putting **any** `*.arpa` web app behind Keycloak SSO.

### 3a. Build Caddy with caddy-security
`services/caddy/Dockerfile` — add to the `xcaddy build`:
```dockerfile
RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/greenpau/caddy-security
```

### 3b. ⚠️ Deploy gotcha — `registry.arpa` routes THROUGH Caddy
The private registry is served at `registry.arpa` **by Caddy itself**. During a Caddy
cutover the registry is unreachable, so a swarm task that must *pull* the new Caddy
image gets `No such image` and ingress stays down (circular dependency, observed live).
**Always pre-pull the new image onto the Caddy placement node BEFORE the swap:**
```bash
ssh <caddy-node> docker pull registry.arpa/caddy:cloudflare-authp   # while Caddy is UP
ssh <manager>   docker service update --image registry.arpa/caddy:cloudflare-authp --force caddy_caddy
```
Recovery if it goes down: the old image is still local on the node — revert with
`docker service update --image registry.arpa/caddy:cloudflare caddy_caddy` (falls back
to the cached local image).

### 3c. ⚠️ Keycloak: remove the RSA-OAEP encryption key
caddy-security cannot parse Keycloak's default **`rsa-enc-generated`** key (algorithm
`RSA-OAEP`) in the realm JWKS → `jwks unsupported key algorithm RSA-OAEP`, provisioning
fails. Delete that **encryption** KeyProvider (the RS256 **signing** key the fleet's JWT
auth uses is separate and untouched; encryption keys are only used for JWE, which the
fleet does not request):
```
keycloak-mcp keyc__agent_components delete_components_by_id {realm:master, id:<rsa-enc-generated id>}
```

### 3d. Keycloak client (one portal client, reusable for all apps)
A single confidential client `caddy-authp` (standard flow) with redirect
`http://auth.arpa/oauth2/keycloak/authorization-code-callback` + `http://auth.arpa/*`.

### 3e. Caddyfile (global `security` block + portal + per-app gate)
```caddyfile
{
    # …email, acme_dns…
    order authenticate before respond
    order authorize before reverse_proxy
    security {
        oauth identity provider keycloak {
            # ⚠️ caddy-security uses `realm` as the OAuth URL path segment
            # (/oauth2/<realm>) AND the `transform match realm <realm>` key — it must
            # equal the name in the policy's `set auth url …/oauth2/<realm>` and the
            # transform below (NOT the Keycloak realm, which lives in metadata_url).
            realm keycloak
            driver generic
            client_id caddy-authp
            client_secret <SECRET>
            scopes openid email profile
            metadata_url http://keycloak.arpa/realms/master/.well-known/openid-configuration
        }
        authentication portal authp {
            crypto key sign-verify <RANDOM_64_HEX>
            cookie domain arpa
            cookie insecure on              # .arpa is plain http (no TLS)
            enable identity provider keycloak
            transform user {
                match realm keycloak
                action add role authp/user  # grant every keycloak user the app role
            }
        }
        authorization policy apps_policy {
            set auth url http://auth.arpa/oauth2/keycloak
            allow roles authp/user authp/admin
            inject headers with claims
        }
    }
}

http://auth.arpa { authenticate with authp }     # the portal (all *.arpa resolve to Caddy)

http://freshrss.arpa {
    handle /api/* { reverse_proxy freshrss_freshrss:80 }   # API: token auth — BYPASS the portal
    handle {                                                # Web UI: Keycloak SSO
        authorize with apps_policy
        reverse_proxy freshrss_freshrss:80 {
            header_up X-WebAuth-User {http.auth.user.id}
        }
    }
}
```
The **live** runtime Caddyfile is `/home/apps/caddy/<…>/Caddyfile` (NOT the
`services/caddy/Caddyfile` GitOps source). Edit live, `caddy validate` (rejects a bad
config — the running config persists), then `caddy reload`.

### 3f. App side — FreshRSS `http_auth`
```bash
docker exec $cid php cli/reconfigure.php --auth-type http_auth   # trust X-WebAuth-User
docker exec $cid ./cli/access-permissions.sh
```
FreshRSS reads the `X-WebAuth-User` header; its value must equal a FreshRSS username
(map the OIDC `preferred_username` claim → `admin`). The GReader API password keeps
working under any web `auth_type` (the bypass + token auth), so ingestion is unaffected.

**To add another app:** add an `http://<app>.arpa { handle … authorize with apps_policy
… }` block (bypass any token/API subpaths), set the app to trust the proxy header. No
new Keycloak client — the one `caddy-authp` portal serves all apps.

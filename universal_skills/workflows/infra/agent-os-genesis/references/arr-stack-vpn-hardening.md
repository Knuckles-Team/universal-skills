# arr-stack VPN hardening — gluetun namespace + fail-closed kill-switch

How the **arr-suite** (Step 11, tier **T6**, node **R510**) must be deployed so torrent/indexer
traffic egresses **only** through the VPN and is **blocked** (not leaked) whenever the tunnel is
down. This is the source-of-truth recipe; the live config lives in the `arr-stack` service repo
(`compose.vpn-hardened.yml` + `AGENTS.md`).

## Why (incident 2026-06-16)
An ISP notice was traced to qBittorrent egressing via the **host public IP**. Root cause was the
old **route-override** design: a `lhns/vpn-gateway:/elevate` sidecar rewrote the `vpn` overlay's
default route to a launcher-run gluetun. That is **not fail-closed**:
- **Startup race** — before the sidecar rewrites the route, containers default-route via Swarm's
  `docker_gwbridge` → host public IP; qBittorrent auto-resumes torrents and announces immediately.
- **No app-level kill-switch** — gluetun's firewall only protects traffic *inside its own
  namespace*; the arr containers live in separate namespaces, so if gluetun drops they fall back
  to the gwbridge and leak.
- **DNS leak** — arr containers used Docker's embedded resolver, not the VPN DNS.

Empirically: qBittorrent exit IP == host IP, default route via `docker_gwbridge`, gluetun firewall
irrelevant.

## The hard constraint
**Docker Swarm does NOT support `network_mode: service:`/`container:`.** That is the entire reason
the fragile route-override existed. A real kill-switch requires every protected app to share
gluetun's network namespace — which means running the arr-suite as a **standalone `docker compose`
on R510**, not as a Swarm stack. All arr services are already pinned to R510, so Swarm scheduling
buys nothing here.

## Target design (fail-closed)
- **gluetun** runs directly (qmcgaw/gluetun, `cap_add: NET_ADMIN`, `devices: /dev/net/tun`),
  single-homed on the compose default bridge for a **deterministic WAN route** (do NOT attach it to
  multiple overlays — multi-homing reintroduces the default-route ambiguity that caused the leak).
- `FIREWALL=on` — the **fail-closed kill-switch**: no egress unless the tunnel is up.
- `FIREWALL_INPUT_PORTS=<all WebUI ports>` and `FIREWALL_OUTBOUND_SUBNETS=10.0.0.0/24,172.16.0.0/16`
  keep the WebUIs reachable and LAN/overlay management working even when the tunnel is down.
- `DNS_ADDRESS=<VPN DNS>` kills the DNS leak.
- **Every other arr service** uses `network_mode: "service:gluetun"` (no own `networks:`/`ports:`),
  `depends_on: { gluetun: { condition: service_started } }` (NOT `service_healthy` — else the apps
  never start while the tunnel is down and you lose management access).
- **gluetun publishes every WebUI port** on the R510 host; **Caddy** reverse-proxies each `*.arpa`
  host to `10.0.0.10:<port>` (replacing the old `arr-stack_<svc>:<port>` swarm-service upstreams).
- Drop `add-vpn-gateway` and the `gluetun-launcher` — obsolete under namespace sharing.
- In the shared namespace the apps reach each other on `localhost`; the VPN DNS won't resolve
  internal `*.arpa`, so cross-app URLs (e.g. unpackerr → sonarr/radarr) must use `http://localhost:<port>`.

## NordVPN credentials
- **OpenVPN** (works today): `VPN_SERVICE_PROVIDER=nordvpn`, `VPN_TYPE=openvpn`, `OPENVPN_USER`/
  `OPENVPN_PASSWORD` = NordVPN **service credentials** (dashboard → Manual setup → Service
  credentials — NOT the account login). `SERVER_COUNTRIES` must be a **literal** (`United States`);
  the old `.env` used a swarm-launcher space hack `United@_@States` which gluetun rejects (crash on
  "country is not valid").
- **WireGuard / NordLynx** (more reliable; optional upgrade): `VPN_TYPE=wireguard` +
  `WIREGUARD_PRIVATE_KEY=<NordLynx key>`. The key comes from NordVPN (access token via the API, or
  `nordvpn`/`wg show nordlynx private-key` on a logged-in machine) — a self-hosted **wg-easy**
  server is unrelated and cannot supply it. Deploy gluetun in a mode that *stays up* (OpenVPN, or a
  valid WG key) — a WireGuard container with a missing/invalid key exits and takes the
  namespace-sharing apps down with it.

## arr MCP gotchas (Step A3/A5 fleet)
- **arr-mcp** must carry every service key: `BAZARR_API_KEY`, `CHAPTARR_API_KEY`, `SEERR_API_KEY`
  are easy to leave blank (they were). Pull keys from each app's config on R510
  (`config.xml`/`config.yaml`/`settings.json`).
- **qbittorrent-mcp**: WebUI auth is **username/password only** (no API key). Point
  `QBITTORRENT_HOST` at the reachable proxy host (`qbittorrent.arpa`), not `127.0.0.1`.
- **Editable au skew (the fleet-wide one):** an MCP whose `/src` imports a symbol newer than the
  image's installed `agent-utilities` (e.g. `run_blocking`) crash-loops with `ImportError`. Fix:
  mount the local au source `-v …/agent-utilities:/au:ro` and set `PYTHONPATH=/au:/src`.
- **chaptarr** runs as uid **99:100** with auth=Basic on **port 8789**; keep its `/config` owned by
  99:100 or it crash-loops on the PID-file write.

## Verify
```
ssh genius@10.0.0.10 'docker exec gluetun wget -qO- http://localhost:8000/v1/publicip/ip'  # VPN IP
ssh genius@10.0.0.10 'docker exec gluetun wget -qO- ifconfig.me'   # must NOT equal host public IP
# kill-switch: stop gluetun -> dependent apps have NO network (fail-closed), recover on start
```

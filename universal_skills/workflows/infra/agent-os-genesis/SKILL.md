---
name: agent-os-genesis
aliases:
  - day0
  - day0_bootstrap_orchestrator
description: >
  Day 0 genesis of the entire Agent OS — agent-first, idempotent unfolding of the
  homelab from bare hosts to a fully wired Docker Swarm. (Formerly
  day0_bootstrap_orchestrator; invoke as "day0" or "agent-os-genesis".) Steps: SSH
  mesh, hardware-driven placement, swarm + overlay networks + custom ingress,
  Caddy/Technitium edge, GitLab/Portainer GitOps, tiered service deploy with
  missing-image tolerance and first-time canaries, cross-service wiring, and
  Knowledge-Graph materialization. Idempotent and re-runnable. Triggers on "day0",
  "day 0 install", "bootstrap the homelab", "stand up the whole Agent OS", "genesis",
  "unfold the fleet from bare hosts".
domain: infrastructure
tags:
  - day0
  - genesis
  - bootstrap
  - infrastructure
  - orchestration
  - swarm
  - dns
  - gitops
  - backups
requires:
  - systems-manager-mcp
  - container-manager-mcp
  - portainer-mcp
  - technitium-dns-mcp
  - tunnel-manager-mcp
  - gitlab-mcp
  - keycloak-mcp
  - caddy-mcp
  - openbao-mcp
  - graph-os
---

# Agent OS Genesis — Day 0 Bootstrap & Multi-Service Wiring Orchestrator

> Renamed from `day0_bootstrap_orchestrator`; the **`day0`** alias still applies.

Agent-first, idempotent unfolding of the homelab from bare hosts to a fully wired
Docker Swarm. This is the repeatable "day-0 (re)install" entrypoint for the Agent OS
in `agent-utilities`: it consumes the Ansible inventory (`~/.config/agent-utilities/inventory.yaml`)
and the `workspace.yml` service manifest, drives the convergence via MCP tools (preferring
the MCP path, with a full-mesh RSA key fallback), and records the resulting topology in the
Knowledge Graph.

## Verified topology (source of truth)

| Host | IP | Swarm role | Notes |
|------|-----|-----------|-------|
| R820 | 10.0.0.13 | **Manager** | Caddy ingress (host-mode 80/443), most MCP servers |
| R710 | 10.0.0.11 | Worker | GitLab CE + registry, high-RAM JVM workloads |
| R510 | 10.0.0.10 | Worker | storage/NAS, arr-stack, Immich DB |
| RW710 | 10.0.0.12 | Worker | misc MCPs |
| GR1080 | 10.0.0.16 | Worker | GPU (CUDA) workloads |
| GB10 | 10.0.0.18 | Worker | Grace-Blackwell; vLLM |

> Placement is **hardware-determined** (Step 4), never hardcoded. The table is the
> expected steady state; the planner may relocate services based on live capacity.

## Networking contract (matches `networks/compose.yml`)

| Network | Subnet | Flags | Purpose |
|---------|--------|-------|---------|
| `internet` | 172.16.0.0/20 | overlay, attachable | outbound egress |
| `caddy` | 172.16.16.0/20 | overlay, attachable, **internal** | service mesh behind ingress |
| `vpn` | 172.16.32.0/20 | overlay, attachable, mtu 1380 | VPN-routed services |
| `cloudflare` | 172.16.48.0/20 | overlay, attachable, **internal** | cloudflare connector |
| `ingress` (custom) | 172.20.0.0/16 | overlay, `--ingress` | replaces Swarm's default ingress |
| `adguard_vlan` | 10.0.0.0/8 | macvlan (`eno4`) | Technitium static IP 10.0.0.199 |

## DNS policy

All `*.arpa` resolve to the **Caddy ingress at `10.0.0.13`** (wildcard `*.arpa` + explicit
`portainer`), which routes by Host header via its static Caddyfile. Intentional exceptions
that point directly at a host/macvlan IP are preserved: `adguard.arpa`/Technitium → 10.0.0.199,
`home-assistant` → its macvlan IP, and per-node `dozzle*`/`container-manager-*` agent records.

> **Troubleshooting:** see [`references/TROUBLESHOOTING.md`](references/TROUBLESHOOTING.md) — a
> symptom→diagnosis→fix runbook for swarm quorum loss, manager re-IP / advertise-addr,
> worker rejoin, DNS `.arpa` repointing, and the **caddy overlay VIP-corruption pitfall**
> (do NOT change a live overlay's subnet in place).

## Failure-handling policy

- **Missing upstream images** — several `*-mcp` services have no image in `registry.arpa` /
  Docker Hub yet. Pre-scan each stack's `image:` for availability; **skip gracefully and add to
  a deferred report** (service → missing image). Never abort a tier for a missing image.
- **First-time / untested stacks** (`apache-jena`/Fuseki, `camunda`, `archimate`/Archi, `kafka`)
  are deployed as **canaries**: deploy in isolation, gate on a health check (env/volumes/ports/
  depends_on sanity + container healthy), and surface logs on failure rather than continuing blindly.

---

## Deployment profiles (agent-utilities day-0)

This orchestrator is **profile-driven**. Step 0 selects a profile, which gates
the remaining steps so the same workflow scales from a laptop to a full swarm:

| Profile | Scope | Steps run |
|---|---|---|
| **tiny** | One host, **zero external infra** — the KG runs in-process. | Step 0 → Step A1 only (collapses to `agent-utilities/scripts/bootstrap.sh`). |
| **single-node-prod** | One host, durable: Postgres/pggraph KG + gateway + the `single-node-prod` connector slice + Caddy; optional OpenBao/Langfuse. No swarm. | Step 0, a Caddy/Portainer subset of Step 7, Step 8 (OpenBao optional), Steps A1–A4. |
| **enterprise** | Full multi-node swarm + all integrations + the entire `*-mcp` fleet. | All steps (1–15 + A1–A4). |

Each integration is an independent toggle gathered in Step 0 —
`pggraph`, `kafka`, `openbao`, `keycloak`, `langfuse` — and any step that depends
on a disabled integration is skipped and reported.

## Steps

### Step 0: deployment-profile
Present the profile + integration questionnaire and resolve the run plan. Read a
default from `~/.config/agent-utilities/inventory.yaml` (`deployment_profile`) if
present, else ask.
- Outputs: `deployment_profile` ∈ {tiny, single-node-prod, enterprise}; integration toggles {pggraph, kafka, openbao, keycloak, langfuse}
- Expected: `profile-selected` — gates every subsequent step.

### Step 1: ssh-bootstrap
[depends_on: Step 0] (profiles: single-node-prod, enterprise — skipped for tiny)
Verify connectivity across inventory hosts and establish passwordless **full-mesh** SSH keys
(every host → every host) as an RSA fallback. Prefer MCP tool usage; the mesh is the safety net.
- Target hosts: `R510`, `R710`, `RW710`, `R820`, `GR1080`, `GB10`
- Requires: `tunnel-manager-mcp`, `systems-manager-mcp`
- Expected: `mesh-reachable`

### Step 2: network-topology-sweep
[depends_on: Step 1]
Scan subnets, NICs, active links, and VLAN profiles on reachable hosts (confirm `eno4` exists for the Technitium macvlan).
- Requires: `tunnel-manager-mcp`, `systems-manager-mcp`
- Expected: `topology-mapped`

### Step 3: hardware-profile-sweep
[depends_on: Step 1]
Discover CPU models/cores, free RAM, disk partitions, and GPU/accelerator devices per host.
- Requires: `systems-manager-mcp`, `tunnel-manager-mcp`
- Expected: `hardware-profiled`

### Step 4: deployment-planner
[depends_on: Step 2, Step 3]
Run the **Deployment Planner** to compute hardware-driven placement: classify services into tiers
(T0–T6), score candidate nodes by capacity/affinity/density, and emit a deterministic manifest.
Bind GPU→GR1080, storage/NAS→R510, JVM/RAM-heavy (`kafka`, `camunda`, `apache-jena`, `archimate`)→
highest-free-RAM node, manager/edge (Caddy)→R820. This manifest drives node labels and compose constraints.
- Inputs: hardware profiles (Step 3), topology (Step 2), `workspace.yml` service list
- Outputs: `golden-deployment.yaml` (node roles, service→node map, network plan)
- Requires: `systems-manager-mcp`, `tunnel-manager-mcp`, `container-manager-mcp`
- Expected: `placement-manifest`

### Step 5: swarm-mesh-provisioner
[depends_on: Step 4]
Converge the swarm + networks via the **Ansible bootstrap playbook** (`networks/bootstrap/swarm.yml`,
driven by `inventory.yaml`; `-e reset_swarm=true` for a destructive clean rebuild) — idempotent and re-runnable:
- `docker swarm init` on **R820 (10.0.0.13)**; join workers `R510`, `R710`, `RW710`, `GR1080`, `GB10`.
- Remove Swarm's auto-created default ingress and create the **custom ingress** `172.20.0.0/16`.
- Create overlay networks per the networking contract: `internet`, `caddy` (internal), `vpn` (mtu 1380), `cloudflare` (internal).
- Requires: `container-manager-mcp`, `tunnel-manager-mcp`
- Expected: `swarm-ready, networks-created`

### Step 6: node-labeling
[depends_on: Step 5]
Apply `docker node update --label-add name=<HOST>` for every node (so `node.labels.name == ${SERVER}`
constraints resolve), plus role labels from the planner (`gpu=true`, `storage=true`, `edge=true`, etc.).
- Requires: `container-manager-mcp`, `tunnel-manager-mcp`
- Expected: `nodes-labeled`

### Step 7: core-edge-deploy
[depends_on: Step 6]
Bring up the bootstrap-critical core **in dependency order**, resolving the registry/GitLab chicken-and-egg
(registry + GitLab must use a publicly pullable base for first boot):
1. `registry` (so `registry.arpa/*` pulls resolve) → 2. `gitlab` (R710) → 3. `technitium-dns` (macvlan, static `10.0.0.199`) → 4. `caddy` (R820, host-mode 80/443) → 5. `portainer`.
- Requires: `portainer-mcp`, `container-manager-mcp`, `technitium-dns-mcp`, `caddy-mcp`
- Expected: `core-edge-up`

### Step 8: secret-vault-manager
[depends_on: Step 7]
Deploy, initialize, and unseal **OpenBao** (KV2 engine) and bring up **Keycloak** (OIDC/SAML).
- Requires: `openbao-mcp`, `keycloak-mcp`
- Expected: `vault-sso-up`

### Step 9: gitlab-repository-seeder
[depends_on: Step 8]
On GitLab CE, auto-provision projects from `workspace.yml`, seed stack compose files, and mint scoped PATs.
- Requires: `gitlab-mcp`
- Expected: `repos-seeded, pats-issued`

### Step 10: portainer-gitops-bind
[depends_on: Step 9]
Bind Portainer stacks to their GitLab repositories using the PATs (GitOps auto-sync).
- Requires: `portainer-mcp`
- Expected: `gitops-bound`

### Step 11: tiered-service-deploy
[depends_on: Step 10]
Deploy all stacks per the placement manifest in dependency tiers (T0→T6), applying the failure-handling policy:
**pre-scan each stack's `image:` for availability → skip+report missing-image `*-mcp` stacks; deploy first-time
stacks (`apache-jena`/Fuseki, `camunda`, `archimate`, `kafka`) as health-gated canaries**.
- T0 Critical edge (DNS, Caddy, VPN, registry) → already up (Step 7), verify
- T1 Core platform (Portainer, GitLab, Keycloak, OpenBao, LGTM)
- T2 Business apps (Twenty, ERPNext, Plane, Mattermost, Firefly, **Camunda**, **Archi**)
- T3 Lifestyle/utility (Mealie, wger, Gramps, FreshRSS, Calibre, Reitti)
- T4 AI/ML (vLLM→GB10, Ollama, XTTS, Faster-Whisper) → GPU nodes
- T5 Agent MCP servers (stateless) — **tolerate missing images**
- T6 Media/NAS-bound (arr-suite, Jellyfin, Immich) → R510
- Data platform (**Kafka**, **Apache-Jena**/Fuseki) → highest-RAM node, canary-gated
- Requires: `portainer-mcp`, `container-manager-mcp`
- Expected: `services-deployed, deferred-report`

### Step 12: dns-record-manager
[depends_on: Step 11]
Apply the DNS policy in Technitium: wildcard `*.arpa` → `10.0.0.13`, explicit `portainer` → `10.0.0.13`,
preserve intentional direct records (`adguard`→.199, `home-assistant`, per-node agents). Verify resolution.
- Requires: `technitium-dns-mcp`
- Expected: `dns-synced`

### Step 13: keycloak-oidc-wiring
[depends_on: Step 12]
Register OIDC SSO clients in Keycloak for SSO-enabled services; store their secrets in OpenBao KV2.
**MCP fleet auth (CONCEPT:OS-5.32):** also create the **`mcp-multiplexer` confidential
client** (audience `agent-services`) via `keycloak-client-onboarder` and store its secret
in OpenBao — this is the service identity the multiplexer uses to reach jwt children
(Step A2). Then load the **baseline eunomia policy** (allow the multiplexer principal,
deny `unknown`) via `eunomia-policy-manager` at `eunomia.arpa` — eunomia fails CLOSED, so
this MUST exist before any MCP enforces jwt.
- Requires: `keycloak-mcp`, `openbao-mcp` (+ skills `keycloak-client-onboarder`, `eunomia-policy-manager`)
- Expected: `sso-wired, mcp-multiplexer-client-created, eunomia-baseline-loaded`

### Step 14: observability-and-backups
[depends_on: Step 13]
Stand up the full LGTM observability standard (CONCEPT:OS-5.23) + Borgmatic backups:
- node-exporter + cAdvisor (global) already give every host + every container metrics.
- Generate the MCP scrape/probe targets and dashboards from the fleet registry:
  `agent-utilities/scripts/gen_prometheus_mcp_targets.py` + `gen_grafana_dashboards.py`.
- Deploy the LGTM stack carrying: the `mcp-fleet` (`/metrics`) + `blackbox-mcp` (`/health`)
  Prometheus jobs, the global `promtail` (container logs → Loki), the full `rules.yml`
  alert set (→ Mattermost), and the provisioned Grafana datasources + dashboards
  (Fleet Overview / Per-Service / Host & Infra).
- Drive per-service wiring via `service-observability-provisioner`.
- Requires: `systems-manager-mcp`, `portainer-mcp` (+ skill `service-observability-provisioner`)
- Expected: `observability-up, mcp-fleet-scraped, dashboards-provisioned, alerts-loaded, backups-scheduled`

### Step 15: graph-os
[depends_on: Step 14]
Materialize the full topology in the Knowledge Graph (`HostNode`, `ContainerStackNode`,
`PlatformService`, network + placement edges), including the **deferred/skipped report** so missing-image
services are tracked for later push+validation.
- Requires: `graph-os`
- Expected: `topology-ingested`

---

## Steps — agent-utilities core (A-series)

These steps install and wire **agent-utilities itself** (its deps, the graph-os
MCP + multiplexer, the `*-mcp` connector fleet, and the integrations). They are
profile-gated; the **tiny** profile runs only Step A1.

### Step A1: agent-utilities-install
[depends_on: Step 0]
Install agent-utilities dependencies on the target host(s): `uv sync` (or
`pip install -e ".[all]"`). For **tiny**, write the zero-infra `.env`
(`GRAPH_BACKEND=tiered`) and run `agent-utilities/scripts/bootstrap.sh` (which
also runs a KG smoke test) — the tiny profile **stops here**.
- Requires: `systems-manager-mcp`
- Expected: `agent-utilities-installed` (tiny: `bootstrap-verified`)

### Step A2: graph-os-and-multiplexer
[depends_on: Step A1] (profiles: single-node-prod, enterprise)
Deploy the **agent-utilities `graph-os` MCP server** (`knucklessg1/agent-utilities`,
container `command: graph-os`, streamable-http :8000) as a Portainer GitOps stack
pinned to the **KG host node (R820)** with `KG_DAEMON_ROLE=host` — it owns the
single consolidated KG daemon. Also start `mcp-multiplexer` federating graph-os +
the connector fleet, and (optionally) the REST gateway `graph-os-daemon` (:8100).
For durable profiles, point `GRAPH_DB_URI` at the pggraph tier (Step A4).

**Multiplexer outbound auth (CONCEPT:OS-5.32):** set `MCP_CLIENT_AUTH=oidc-client-credentials`,
`OIDC_CLIENT_ID=mcp-multiplexer`, `OIDC_CLIENT_SECRET` (OpenBao ref from Step 13),
`OIDC_AUDIENCE=agent-services` on the multiplexer so it mints + attaches a Keycloak service
token to every jwt child. Without this, children with `AUTH_TYPE=jwt` are unreachable (401)
through the multiplexer. The multiplexer itself stays at its own inbound-auth posture (do
NOT flip it to a jwt child — it is the client).

**Shared agent-utilities config volume (CONCEPT: OS-5.x):** seed an **external**
named volume `agent_utilities_config` (and `agent_utilities_data`) on the KG host
with the bare-metal `~/.config/agent-utilities/config.json`, and mount it at
`/root/.config/agent-utilities` in graph-os. This is the single source of
config (models, backends, secrets, OTel/Langfuse) — the same volume a bare-metal
install reads. Any **config-aware** `*-mcp` (those that use agent-utilities
models / KG / secrets — e.g. `data-science-mcp`, `scholarx-mcp`,
`repository-manager-mcp`, `emerald-exchange-mcp`) mounts the **same** volume and
is **co-located on the KG host** so the node-local named volume resolves (or back
it with a shared/NFS driver). Thin API-wrapper connectors (github, gitlab,
servicenow, …) do **not** need it — they take their own creds via stack env.
- Requires: `graph-os`, `container-manager-mcp`, `portainer-mcp`
- Expected: `graph-os-up, multiplexer-up, config-volume-seeded`

### Step A3: mcp-fleet-deploy
[depends_on: Step A2] (profiles: single-node-prod, enterprise)
Deploy the `*-mcp` connector fleet from
`agent-utilities/deploy/mcp-fleet.registry.yml`, filtered to services whose
`profiles:` include the active profile. Each is a per-service Portainer stack
(streamable-http, container port `8000` → its registry `host_port`) bound to Git
for GitOps auto-sync via `portainer-sync-agent`. Apply the missing-image
Failure-handling policy. (Regenerate the registry with
`python agent-utilities/scripts/gen_mcp_fleet_registry.py --agents-dir <…>/agents`.)

**Auth + deploy artifact (CONCEPT:OS-5.32 / OS-5.23):** the generated composes ship
`AUTH_TYPE=jwt` + eunomia by default (from `gen_mcp_service_stacks.py` / `gen_editable_compose.py`),
and every service exposes unauthenticated `/metrics` + `/health`. Deploy the **editable**
`compose.dev.yml` (set Portainer `ConfigFilePath=compose.dev.yml`): one container per MCP,
source-mounted at `/src`, pinned to the source node — edits go live on restart. Children
are reachable because the multiplexer presents its service token (Step A2). Flip jwt in
**phased waves** (read-only → data → sensitive; `portainer-mcp` last; never the multiplexer),
verifying multiplexer reachability after each wave.

**Gotchas baked in from live rollout (see `references/TROUBLESHOOTING.md`):**
- **eunomia needs the fastmcp-3.x compat build** (§9): without `apply_fastmcp_enabled_compat()`
  in the deployed agent-utilities, every `tools/call` on a eunomia service errors. Don't flip
  `EUNOMIA_TYPE=remote` onto images that predate that build.
- **Stack env is inert unless the compose passes it** (§10): set BOTH the stack Env value AND
  `- VAR=${VAR}` in the compose `environment:` (tokens, connector URLs).
- **Healthcheck port must equal `PORT`** (§11): a mismatch crash-loops the service to 502;
  prefer a `socket.create_connection(('localhost', PORT))` check.
- **Mount the connector's working data** (§13): repository-manager → workspace +
  `WORKSPACE_PATH`; container/tunnel-manager → `inventory.yaml` + `~/.ssh`. A missing import
  module is a packaging fix (add dep + rebuild), not a mount.
- After restarting any child, **reconnect the multiplexer** before re-validating (§12) — stale
  sessions hang tool calls 300s.
- Requires: `portainer-mcp`, `container-manager-mcp`
- Expected: `mcp-fleet-deployed, auth-on, metrics-exposed, deferred-report`

### Step A4: integrations-wiring
[depends_on: Step A3] (toggle-gated)
Wire **only the enabled** integrations into the agent-utilities config: `pggraph`
(`GRAPH_DB_URI`), `kafka` (`QUEUE_BACKEND=kafka` + `KAFKA_BOOTSTRAP_SERVERS`),
`openbao` (`SECRETS_VAULT_URL` + `VAULT_AUTH_METHOD`), `keycloak`
(`AUTH_JWT_JWKS_URI` / OIDC), `langfuse` (`LANGFUSE_*` + `ENABLE_OTEL`). Disabled
toggles are skipped and reported.
- Requires: `openbao-mcp`, `keycloak-mcp`
- Expected: `integrations-wired`

### Step A5: mcp-config-rewire (streamable-http, no stdio)
[depends_on: Step A3] (profiles: single-node-prod, enterprise)
Once the fleet is deployed, **back up** every `mcp_config*.json` (workspace +
`~/.config/agent-utilities/mcp_config.json`) to a timestamped dir, then **rewire**
each connector entry from a local **stdio** spawn
(`{"command": ".venv/bin/<name>", ...}`) to the deployed **streamable-http**
endpoint (`{"transport": "streamable-http", "url": "http://<name>.arpa/mcp"}`).
We no longer run the connectors as stdio servers. `graph-os` likewise points at
its R820 streamable-http endpoint. Only rewire entries whose container is live
(use the deferred/skipped report from Step A3); leave the rest stdio until
deployed. Reload the multiplexer.
**Auth note (CONCEPT:OS-5.32):** rewired entries are remote `streamable-http` children that
enforce jwt — leave their `headers` empty; the multiplexer's service token (Step A2) is
attached automatically. Do NOT bake per-child bearer tokens into `mcp_config.json`.
- Requires: `container-manager-mcp`
- Expected: `mcp-config-rewired, stdio-retired`

### Step A6: verify auth + observability end-state
[depends_on: Step A5] (profiles: single-node-prod, enterprise)
Assert the realized end-state (CONCEPT:OS-5.32 / OS-5.23):
- Each jwt MCP rejects unauthenticated calls: `curl -s -o /dev/null -w '%{http_code}'
  -X POST http://<svc>.arpa/mcp` → `401`.
- The multiplexer can call a tool on a jwt child (service token attached) → success.
- **Validate at the TOOL-CALL level, not just `initialize`** — `initialize`/`tools/list`
  passing hides per-call failures (eunomia, missing module, bad URL). Run a full host-side MCP
  session with the A0 token (`initialize`→`initialized`→`tools/list`→`tools/call`) per service;
  see `references/TROUBLESHOOTING.md` §8. In particular, after enabling `EUNOMIA_TYPE=remote`,
  confirm a real `tools/call` returns data and NOT `'FunctionTool' object has no attribute
  'enabled'` (the fastmcp-3.x eunomia break — §9; requires the agent-utilities compat build).
- `/metrics` returns Prometheus exposition: `curl http://<svc>.arpa/metrics`; a tool call
  increments the per-tool counter.
- Prometheus shows `up{job="mcp-fleet"}==1` and `probe_success{job="blackbox-mcp"}==1` for
  live services; Grafana "MCP Fleet Overview" is populated; stopping a service fires
  `McpServiceDown`/`McpProbeFailed` to Mattermost.
- Requires: `portainer-mcp`, `systems-manager-mcp`
- Expected: `auth-enforced, multiplexer-reachable, metrics-live, dashboards-populated, alerts-firing`

---
name: agent-utilities-process-integration
aliases:
  - camunda-aris-setup
  - process-integration
  - connect-camunda
  - connect-aris
description: >
  One guided, config-complete path to connect Software AG ARIS and Camunda to the
  agent-utilities Knowledge Graph — bidirectionally and OWL/RDF-natively. Walks the
  user through every connection/credential option (Camunda 7 Engine REST or Camunda 8
  Zeebe/Operate/Tasklist; ARIS Connect/Enterprise/Cloud REST with OAuth2, bearer, or
  basic auth and per-tenant path overrides), deploys the camunda-mcp and aris-mcp
  connectors, INGESTS processes into the KG (graph_ingest materialize_source) so they
  become canonical ArchiMate :BusinessProcess/:BusinessTask/:flowsTo objects reasoned
  over in OWL, and turns on the OUTBOUND enrichment (graph_analyze process_writeback,
  KG_PROCESS_WRITEBACK) that writes KG intelligence back onto Camunda instances and
  ARIS models. Composes the existing agent-utilities-deployment and agent-os-genesis
  skills for the base platform rather than duplicating them. Use when the user says
  "connect Camunda", "connect ARIS", "ingest our processes", "set up the process
  integration", "enrich Camunda/ARIS from the knowledge graph", "configure camunda-mcp
  / aris-mcp". Do NOT use to deploy the base platform from scratch (use
  agent-utilities-deployment) or for bare-host swarm bootstrap (use agent-os-genesis).
domain: infrastructure
tags:
  - camunda
  - aris
  - bpmn
  - process-integration
  - knowledge-graph
  - ontology
  - owl
  - enrichment
requires:
  - graph-os
---

# Connect Camunda + ARIS to the Knowledge Graph (bidirectional, OWL/RDF-native)

The one runbook to wire **Camunda** (BPMN) and **Software AG ARIS** (EPC/EA) into the
agent-utilities Knowledge Graph and back out again — **every connection option
considered**. It composes existing skills/tools rather than re-implementing them:
[`agent-utilities-deployment`](../agent-utilities-deployment/SKILL.md) (base platform),
[`agent-os-genesis`](../agent-os-genesis/SKILL.md) (multi-node swarm), `docker-compose-operator`
(deploy connectors), `secret-vault-manager` (credentials), and the `graph_ingest` /
`graph_analyze` MCP tools (ingest + writeback).

Architecture reference: `agent-utilities/docs/architecture/camunda_aris_kg_integration.md`.

## What you get

```
Camunda 7/8 ─┐                      ┌─ kg_intelligence variables → Camunda instances
ARIS REST   ─┤  → KG (one ArchiMate │
             │     ontology, OWL    │
             └→ :BusinessProcess /  │
                :BusinessTask /     └─ kg_intelligence attributes → ARIS models
                :flowsTo, reasoned)
```

- **Inbound:** processes become canonical `:BusinessProcess` / `:BusinessTask` /
  `:flowsTo` objects; a Camunda process and its ARIS twin reconcile via `ALIGNED_WITH`
  and are reasoned over together.
- **Outbound:** the KG's per-process intelligence (capability/code lineage, OWL
  inferences, incidents, glossary/data lineage) is written back onto live Camunda
  instances and ARIS models.

## Prerequisites
- **graph-os** (agent-utilities) running — gateway + MCP. If not, run
  `agent-utilities-deployment` first.
- Network reachability to your Camunda engine and/or ARIS tenant.
- The connectors: `camunda-mcp` and `aris-mcp` (`pip install camunda-mcp aris-mcp`, or
  deploy as fleet services — see Step 3).

## Step 1 — Decide scope

Ask the user:
1. **Which systems?** Camunda only, ARIS only, or both.
2. **Direction?** Inbound (ingest → KG), outbound (enrich → Camunda/ARIS), or both.
3. **Camunda platform?** 7 (Engine REST) or 8 (Zeebe/Operate/Tasklist).
4. **ARIS edition + auth?** Connect on-prem / Enterprise / Cloud; OAuth2 vs token vs basic.

## Step 2 — Configure connection & credentials

Store secrets via `secret-vault-manager` (OpenBao/Vault) or a connector `.env`. **Every
option:**

### Camunda (`camunda-mcp` — read `auth.get_client()`)
| Variable | Purpose |
|---|---|
| `CAMUNDA_PLATFORM` | `7` or `8` (default `7`) |
| `CAMUNDA_SSL_VERIFY` | verify TLS (default `True`) |
| `CAMUNDA7_URL` | Engine REST base (e.g. `http://camunda.arpa/engine-rest`) |
| `CAMUNDA7_TOKEN` | bearer, **or** |
| `CAMUNDA7_USERNAME` / `CAMUNDA7_PASSWORD` | basic auth |
| `CAMUNDA8_ZEEBE_REST_URL` / `CAMUNDA8_OPERATE_URL` / `CAMUNDA8_TASKLIST_URL` | C8 REST endpoints |
| `CAMUNDA8_CLIENT_ID` / `CAMUNDA8_CLIENT_SECRET` / `CAMUNDA8_OAUTH_URL` / `CAMUNDA8_AUDIENCE` | C8 OAuth2 client-credentials |

### ARIS (`aris-mcp` — read `auth.get_client()`)
| Variable | Purpose |
|---|---|
| `ARIS_API_BASE` | REST base URL / tenant API root (default `http://localhost/abs/api`) |
| `ARIS_SSL_VERIFY` | verify TLS (default `True`) |
| `ARIS_OAUTH_URL` / `ARIS_CLIENT_ID` / `ARIS_CLIENT_SECRET` / `ARIS_TENANT` | OAuth2 client-credentials (preferred) |
| `ARIS_TOKEN` | static bearer (alt) |
| `ARIS_USERNAME` / `ARIS_PASSWORD` | basic (alt) |
| `ARIS_PATHS_JSON` | per-tenant REST path overrides (keys: models, model, model_objects, model_connections, model_attributes, object_attributes) |
| `ARIS_ENABLE_WRITE` | allow attribute writes (default `False`; required for outbound) |

> **ARIS tenant differences (confirm first).** ARIS Connect-on-prem and ARIS Cloud have
> different base paths and auth. The defaults follow the common Connect ABS REST layout.
> Probe `GET {ARIS_API_BASE}/models` (with auth) to confirm the model-inventory shape;
> if objects/connections live under different paths, set `ARIS_PATHS_JSON`. Confirm the
> API tier permits attribute writes before relying on outbound to ARIS.

## Step 3 — Deploy the connectors

- **Local / stdio:** `uv run camunda-mcp` and `uv run aris-mcp` (see each package's
  `mcp_config.json`).
- **Fleet service:** the connectors are registered in
  `agent-utilities/deploy/mcp-fleet.registry.yml` (`camunda-mcp`, `aris-mcp`,
  `enterprise` profile). Deploy with `docker-compose-operator` / the fleet compose, then
  confirm health: `GET http://<host>:<port>/health`.

The KG resolves these connectors **in-process** via each package's `auth.get_client()`,
so the same environment that runs the gateway must carry the connection vars above.

## Step 4 — Ingest processes INTO the KG (inbound)

Use the `graph_ingest` MCP tool (or `POST /graph/ingest/materialize-source`):

```
graph_ingest(action="materialize_source", corpus_name="camunda")
graph_ingest(action="materialize_source", corpus_name="aris")
```

Each call runs the extractor over the live connector, persists
`:BusinessProcess` / `:BusinessTask` / `:flowsTo`, then runs one OWL reasoning cycle.
Response reports `nodes`, `edges`, `inferred_edges`, `new_topics`. Re-run any time to
refresh (idempotent by node id).

Verify: `graph_search`/`graph_query` for `bpmn_process:*` and `aris_model:*` nodes;
`graph_analyze(action="enrichment_coverage")` for per-source counts.

## Step 5 — Enrich data back INTO Camunda & ARIS (outbound)

1. Enable the gate: set `KG_PROCESS_WRITEBACK=1` in the gateway environment (and
   `ARIS_ENABLE_WRITE=True` for ARIS writes).
2. Run:

```
graph_analyze(action="process_writeback", target="both")   # or "camunda" / "aris"
# optional: query="bpmn_process:invoice,aris_model:M1" to limit to specific processes
```

This writes a single `kg_intelligence` payload (capability/code lineage, OWL inferences,
incidents, glossary/data lineage) as a Camunda **process-instance variable** on every
running instance and/or an ARIS **model attribute**. Writes are hash-idempotent. Note:
Camunda 7 writeback targets **running instances** (no runtime extension-property write),
so start an instance to see the variable.

## Step 6 — Verify end-to-end

- Inbound, live: `CAMUNDA7_URL=... pytest -m live agent-utilities/tests/integration/test_camunda_live.py`.
- Outbound: read back a running instance's variables and confirm `kg_intelligence` is
  present (Camunda Cockpit or `GET /engine-rest/process-instance/{id}/variables`).
- Reasoning: `graph_analyze` / the ontology reasoning surface shows `ALIGNED_WITH`
  identity between a Camunda process and its ARIS twin.

## Notes & guardrails
- Connection creds are **connector** config (live in `camunda-mcp`/`aris-mcp` env), not
  agent-utilities config. Only the outbound gate `KG_PROCESS_WRITEBACK` is an
  agent-utilities flag.
- Keep ARIS writes off (`ARIS_ENABLE_WRITE=False`) until the tenant's API write tier is
  confirmed.
- For the base platform / multi-node swarm, defer to `agent-utilities-deployment` and
  `agent-os-genesis` — this skill assumes a running KG.

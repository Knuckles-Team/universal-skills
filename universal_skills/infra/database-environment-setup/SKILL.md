---
name: database-environment-setup
description: >
  Provision the agent-utilities database environment end-to-end from credentials:
  push the ontology to Stardog (prod) or a local SPARQL endpoint (dev), stand up a
  Postgres carrying Apache AGE + pgvector + ParadeDB pg_search, wire the durable
  backend, and backfill graph relationships into AGE. Resolves secrets from
  OpenBao/Vault (with .env fallback). Prompts for environment (prod/dev) and
  Postgres mode (combined image vs existing/managed). Use when the user wants to
  "set up Stardog", "host my ontology over SPARQL", "install pg-age/pgvector/
  paradedb", "backfill into AGE", "connect my postgres", or "set up my database
  environment". Do NOT use for OpenBao unseal/seed alone — use secret-vault-manager;
  or generic container deploys — use docker-compose-operator.
domain: infrastructure
tags:
  - stardog
  - sparql
  - postgres
  - apache-age
  - pgvector
  - paradedb
  - ontology
  - knowledge-graph
requires:
  - graph-os
---

# Database Environment Setup (Stardog + pg-age)

Stand up the two database environments agent-utilities is built around — **prod**
(Stardog) and **dev** (local SPARQL) — and durably backfill the graph into Apache
AGE. This skill is the guided front-end to the `setup-databases` CLI / the
`graph_configure` MCP actions `setup_databases` & `verify_databases`. The full
narrative reference is [`docs/recipes/databases.md`](../../../../agent-utilities/docs/recipes/databases.md)
in agent-utilities.

## Prerequisites

- **graph-os** (agent-utilities) — the `graph_configure` tool and `setup-databases`
  console script. Install it with `pip install agent-utilities[owl,postgres]`
  (add `stardog` for the prod path).
- **openbao-mcp** *(optional)* — to resolve Vault/OpenBao secrets. Falls back to `.env`.
- **container-manager-mcp** *(optional)* — to build/deploy the combined Postgres image.

## Steps

### Step 1 — Resolve credentials (OpenBao/Vault, `.env` fallback)
Prefer OpenBao/Vault. If `SECRETS_BACKEND=vault` is set, reuse **secret-vault-manager**
to confirm the vault is unsealed and the required paths exist, then reference them
with `vault://` (e.g. `GRAPH_DB_URI=vault://agents/db/pg_age#dsn`). Otherwise read a
local `.env`. Collect: the **Postgres DSN** and (prod only) `STARDOG_ENDPOINT`,
`STARDOG_DATABASE`, `STARDOG_USER`, `STARDOG_PASSWORD`.

### Step 2 — Prompt: environment
Ask **prod** (Stardog present) or **dev** (no Stardog → local `/api/sparql`, optional
Jena Fuseki).

### Step 3 — Prompt: Postgres mode
- **managed_image** — a Postgres we control. Build/deploy the combined image
  `docker/pg-age-full.compose.yml` (AGE + pgvector + pg_search) via
  **docker-compose-operator**. All three extensions guaranteed.
- **existing** — an externally-managed Postgres. Connect only; `CREATE EXTENSION`
  what's permitted and **report** any of `age`/`pg_search` that need superuser +
  `shared_preload_libraries` and are therefore unavailable. Degrade gracefully
  (pgvector-only, or point AGE/full-text at a second instance).

### Step 4 — Provision & verify Postgres
Run extension verification:
`graph_configure(action="verify_databases", config_value='{"dsn":"<DSN>"}')`
(or `setup-databases --verify --dsn <DSN>`). Confirm `age`/`vector`/`pg_search`.

### Step 5 — Run the end-to-end setup
Invoke the driver, which wires the backend (`GRAPH_DB_URI`+`GRAPH_PG_AGE=1`+
`GRAPH_BACKEND=tiered`), publishes the ontology, backfills into AGE, and smoke-tests
SPARQL:

```
graph_configure(
  action="setup_databases",
  config_key="<prod|dev>",
  config_value='{"postgres_mode":"<managed_image|existing>","dsn":"<DSN>","sparql_target":"<stardog|builtin|fuseki>"}'
)
```

CLI equivalent: `setup-databases --profile <prod|dev> --postgres-mode <…> --dsn <DSN>`.

### Step 6 — Report & confirm consumption
Surface the step report (`verify_postgres` → `configure_backend` → `publish_ontology`
→ `register_stardog_mirror` (prod) → `backfill_to_age` → `verify_sparql`). Tell the
user the SPARQL URL to consume:
- **prod**: `$STARDOG_ENDPOINT/$STARDOG_DATABASE/query`
- **dev**: the gateway's `GET/POST /api/sparql` (or the Fuseki dataset).
Confirm the backfill is consistent (`reconcile.nodes_missing == 0`).

### Step 7 — Populate Stardog with INSTANCE DATA (not just the ontology)
Step 5 pushes the **ontology** (TBox). To also get the KG's **data** — the nodes/edges
from sources like LeanIX and ServiceNow — Stardog is a first-class SPARQL data backend.
Data is partitioned into `urn:source:<system>` named graphs so each source is a slice
you can push, query, or re-ingest on its own. Two modes (use both):

- **Continuous (live mirror):** the prod profile registers Stardog as a
  `role="mirror"` connection by default, so under `GRAPH_BACKEND=tiered` every KG write
  — including each source sync — fans out into Stardog. (Set `--no-mirror-data` /
  `mirror_data_to_stardog=false` to publish only the ontology.) Backfill existing data
  with `graph_configure(action="reconcile")`.
- **On-demand** via `graph_configure` (REST twin: `POST /graph/configure`):
  - `action="push_to_stardog"`, `config_value='{"sources":["leanix","servicenow"]}'`
    (omit `sources` to push everything) — writes nodes/edges into their named graphs.
  - `action="stardog_sparql"`, `config_value='{"query":"SELECT ?s ?p ?o WHERE { GRAPH <urn:source:leanix> { ?s ?p ?o } } LIMIT 25"}'`
    — run any SPARQL SELECT/ASK/CONSTRUCT/UPDATE.
  - `action="pull_from_stardog"`, `config_value='{"source":"leanix"}'` — re-ingest a
    named graph back into the KG.

Reuses the same `STARDOG_*` credentials from Step 1; no new env flags.

## Notes
- No new environment flags are introduced — every key (`GRAPH_DB_URI`, `GRAPH_PG_AGE`,
  `GRAPH_BACKEND`, `STARDOG_*`, `SECRETS_*`/`VAULT_*`) already exists.
- The combined image requires AGE and ParadeDB to share a Postgres major; if they
  can't, fall back to two instances (AGE+pgvector via `docker/pg-age`, ParadeDB
  separately) and pass each its own DSN.

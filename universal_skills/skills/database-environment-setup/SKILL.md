---
name: database-environment-setup
skill_type: skill
description: >-
  Provision the database environment from credentials: push the ontology to Stardog or a local SPARQL endpoint, stand up Postgres with AGE, pgvector and pg_search, wire the durable backend, backfill AGE. Use to set up Stardog, host an ontology over SPARQL, or connect Postgres. Do NOT use for OpenBao unseal alone (secret-vault-manager) or generic container deploys (docker-compose-operator).
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
  - arbora
metadata:
  version: '1.6.2'
---

# Database Environment Setup (Stardog + pg-age)

Scope: Provision the meristem database environment end-to-end from credentials: push the ontology to Stardog (prod) or a local SPARQL endpoint (dev), stand up a Postgres carrying Apache AGE + pgvector + ParadeDB pg_search, wire the durable backend, and backfill graph relationships into AGE. Resolves secrets from OpenBao/Vault (with .env fallback). Prompts for environment (prod/dev) and Postgres mode (combined image vs existing/managed). Use when the user wants to "set up Stardog", "host my ontology over SPARQL", "install pg-age/pgvector/ paradedb", "backfill into AGE", "connect my postgres", or "set up my database environment". Do NOT use for OpenBao unseal/seed alone — use secret-vault-manager; or generic container deploys — use docker-compose-operator.

Stand up the two database environments meristem is built around — **prod**
(Stardog) and **dev** (local SPARQL) — and durably backfill the graph into Apache
AGE. This skill is the guided front-end to the `setup-databases` CLI / the
`graph_configure` MCP actions `setup_databases` & `verify_databases`. The detailed
recipe is owned by the `meristem` package at
`docs/recipes/databases.md`; it is not bundled with this universal skill. Consult
the compatible package checkout only when package-specific implementation detail
is needed.

## Prerequisites

- **arbora** (meristem) — the `graph_configure` tool and `setup-databases`
  console script. Install it with `pip install meristem[owl,postgres]`
  (add `stardog` for the prod path).
- **openbao-mcp** *(optional)* — to resolve Vault/OpenBao secrets. Falls back to `.env`.
- **container-manager-mcp** *(optional)* — to build/deploy the combined Postgres image.

## Steps

1. Resolve the credentials from OpenBao or `.env` (Step 1). Verify that `grep -c '^STARDOG_ENDPOINT=' .env` is non-zero for prod or that the `vault://` path resolves with `secret-vault-manager`.
2. Choose the environment, prod or dev (Step 2), and the Postgres mode, `managed_image` or `existing` (Step 3). Verify that both answers are recorded before provisioning starts.
3. Verify the Postgres extensions with `graph_configure(action="verify_databases", config_value='{"dsn":"<DSN>"}')` (Step 4). Verify that `age`, `vector` and `pg_search` are reported present, or that missing ones are listed.
4. Run the end-to-end setup with `graph_configure(action="setup_databases", config_key="<prod|dev>", ...)` (Step 5). Verify that the step report runs through `verify_postgres`, `configure_backend`, `publish_ontology`, `backfill_to_age` and `verify_sparql` without a failed step.
5. Confirm consumption by querying the SPARQL URL and checking `reconcile.nodes_missing == 0` (Step 6). Verify that a trivial `SELECT` against the endpoint returns rows.
6. Optionally push instance data with `graph_configure(action="push_to_stardog")` (Step 7). Verify that `action="stardog_sparql"` returns rows from the `urn:source:<system>` graph.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `age` or `pg_search` missing on an existing Postgres | Extension needs superuser and `shared_preload_libraries` | Use `managed_image` mode with `docker/pg-age-full.compose.yml`, or point AGE and full-text at a second instance with its own DSN |
| Vault paths cannot be resolved | Vault is sealed or the path is wrong | Unseal with `secret-vault-manager`, correct the `vault://` path, or fall back to `.env` |
| `reconcile.nodes_missing` is above zero | The AGE backfill was partial | Run `graph_configure(action="reconcile")` and check the count again |
| SPARQL smoke test fails on prod | Wrong `STARDOG_ENDPOINT` or `STARDOG_DATABASE` | Correct both values in the credentials, then rerun `setup_databases` |


## Notes
- No new environment flags are introduced — every key (`GRAPH_DB_URI`, `GRAPH_PG_AGE`,
  `GRAPH_BACKEND`, `STARDOG_*`, `SECRETS_*`/`VAULT_*`) already exists.
- The combined image requires AGE and ParadeDB to share a Postgres major; if they
  can't, fall back to two instances (AGE+pgvector via `docker/pg-age`, ParadeDB
  separately) and pass each its own DSN.

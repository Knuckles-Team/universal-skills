---
name: leanix-integration
aliases:
  - leanix-sync
  - mirror-leanix
  - ea-integration
description: >
  Drive the end-to-end SAP LeanIX ⇄ Knowledge Graph integration: discover the live
  LeanIX metamodel and mirror it natively as OWL/RDF, mirror every fact sheet and
  relationship into the KG, keep it in sync with bite-sized deltas (watermark poll +
  webhook + nightly reconcile), and backfeed KG-derived knowledge (inferred
  relationships, enrichment, new fact sheets) back into LeanIX — fail-closed and
  dry-run-first. Use when the user says "ingest LeanIX", "mirror LeanIX into the KG",
  "sync LeanIX", "discover the LeanIX metamodel", "backfeed to LeanIX", "set up our
  EA / enterprise architecture in the graph". Composes the agent-utilities graph-os
  tools (ontology_leanix_sync, leanix_sync, leanix_writeback); it does NOT
  re-implement them. The enterprise self-setup (agent-utilities-deployment /
  agent-os-genesis) delegates the EA data-source step here. Do NOT use for generic
  database setup (database-environment-setup) or bare-host bootstrap (agent-os-genesis).
domain: infrastructure
tags:
  - leanix
  - enterprise-architecture
  - knowledge-graph
  - ontology
  - owl
  - sync
  - backfeed
requires:
  - graph-os
---

# LeanIX ⇄ Knowledge Graph Integration

One runbook to take LeanIX from "external SaaS" to a **native, reasoned, in-sync,
write-back-capable** part of the knowledge graph. It composes the graph-os MCP tools;
the full reference + troubleshooting matrix lives in the agent-utilities guide
**`docs/guides/leanix-integration.md`** — read it when a step misbehaves.

> **Integration:** `agent-utilities-deployment` (self-setup) and `agent-os-genesis`
> (day-0) call this skill for the EA data-source step. You can run it standalone, or
> as a subset of a larger deployment. It needs only a reachable graph-os engine +
> LeanIX credentials — no other deployment step is a hard prerequisite.

## Prerequisites

- A running **graph-os** engine/gateway (the `leanix_*` / `ontology_leanix_sync`
  MCP tools are reachable). If not, run `agent-utilities-deployment` first.
- LeanIX base URL + a **technical-user API token** with read (and, for backfeed,
  write) scope.

## Step 1 — Configure credentials

Ensure these are in `~/.config/agent-utilities/config.json` (or the deployment's
secret store via `secret-vault-manager`):

```json
{
  "LEANIX_URL": "https://<workspace>.leanix.net",
  "LEANIX_TOKEN": "<api-token>",
  "LEANIX_VERIFY_SSL": true,
  "LEANIX_ENABLE_WRITE": false
}
```

Confirm resolution before continuing:

```python
from agent_utilities.ecosystem.ea_clients import get_leanix_client
assert get_leanix_client() is not None, "LEANIX_URL/LEANIX_TOKEN not configured"
```

## Step 2 — Discover the metamodel → OWL

Preview, then apply. This regenerates `ontology_leanix.ttl` (every fact sheet type,
relation, field) and registers the types for OWL promotion.

```
graph-os call ontology_leanix_sync {"dry_run": true}    # review generated OWL
graph-os call ontology_leanix_sync {"dry_run": false}   # apply
```

## Step 3 — Mirror the fact-sheet graph

```
graph-os call leanix_sync {"mode": "full"}
```

Verify:

```cypher
MATCH (n) WHERE n.domain = 'leanix' RETURN n.type, count(*) ORDER BY count(*) DESC
```

Each node carries `externalToolId` + `domain="leanix"` (the federation key).

## Step 4 — Keep it in sync

- **Delta poll** (only changes since the watermark): `graph-os call leanix_sync {"mode": "delta"}`
- **Reconcile** (tombstone deletions): `graph-os call leanix_sync {"mode": "reconcile"}`
- **Schedule** both via `deploy/schedules.yml` — `leanix-delta-sync` (every 30 min)
  and `leanix-reconcile` (nightly) ship enabled. Confirm with `/cron calendar`.
- **Webhook (optional, near-real-time):** point a LeanIX webhook at an endpoint that
  calls `leanix_sync {"mode": "delta", "ids_json": "[\"<changed-id>\"]"}`.

## Step 5 — Backfeed into LeanIX (optional, fail-closed)

**Dry-run first** — live writes require `LEANIX_ENABLE_WRITE=true`.

```
graph-os call leanix_writeback {"inferences_json": "[{\"source\":\"app:a1\",\"rel_type\":\"REL_APPLICATION_TO_IT_COMPONENT\",\"target\":\"itcomponent:ic1\"}]", "dry_run": true}
# review proposals, then set LEANIX_ENABLE_WRITE=true and:
graph-os call leanix_writeback {"inferences_json": "[...]", "dry_run": false}
```

Inferred relations are tagged `agent-utilities:inferred` (reversible). Enrichment and
fact-sheet creation are supported via `enrichments_json` / `creations_json`.

## Verification checklist

- `ontology_leanix_sync dry_run=false` → `status: completed`, classes > 0.
- `leanix_sync mode=full` → `nodes_hydrated` > 0; Cypher count by type looks right.
- `leanix_sync mode=delta` twice → second run hydrates only changed sheets.
- `leanix_writeback dry_run=true` → proposals listed, nothing written.
- `python scripts/check_surface_parity.py` (in agent-utilities) → 0 unexposed.

## Troubleshooting (quick)

| Symptom | Fix |
|---|---|
| `get_leanix_client()` is `None` | Set `LEANIX_URL` + `LEANIX_TOKEN` in config.json. |
| `ontology_leanix_sync` → `skipped: empty metamodel` | Host unreachable / bad token / SSL — check URL, re-mint token, set `LEANIX_VERIFY_SSL=false` for self-signed. |
| `leanix_sync` returns 0 nodes | Run `mode=full`; verify the token has read scope. |
| Generated types not reasoned over | Run `ontology_leanix_sync dry_run=false`, then restart the engine/daemon. |
| Delta re-pulls everything | Missing/non-monotonic `updatedAt`; ensure the `LeanixSyncState` node persists (still correct, just not incremental). |
| Deletions linger | Run/enable `leanix_sync mode=reconcile`. |
| `leanix_writeback` → `refused` | Intended — set `LEANIX_ENABLE_WRITE=true` after reviewing the dry-run. |

For the full matrix and architecture map, see
`docs/guides/leanix-integration.md` in agent-utilities.

## Safety

LeanIX is the system-of-record. Ingest/delta never write to LeanIX. Backfeed is
fail-closed (`LEANIX_ENABLE_WRITE`) and dry-run-by-default; auto-creating fact sheets
is the highest-risk action — supply `creations_json` explicitly and review the
dry-run first.

# Epistemic-graph authorization reference

Raw enumerations behind the authorization model in the parent
[`SKILL.md`](../SKILL.md) §1: the complete `authz_action` vocabulary the
capability ledger actually declares, the 45 actions a bare read-tier scope
clears and their method counts, the two disagreeing definitions of "admin" and
exactly which actions fall between them, and the re-derivation scripts for
every number §1 quotes. §1 itself carries the model, the chokepoint, the
bypasses and the three findings and is self-sufficient without this file; open
this one when you need the lists rather than the rules.

## The `authz_action` vocabulary

**103 distinct `authz_action` strings over 412 `MethodPolicy` rows**, none of
them `kg:`-prefixed. `kg:read` / `kg:write` / `kg:admin` are *scopes a caller
holds*, never actions a method declares — the two vocabularies are disjoint and
conflating them is the fastest way to misread this model.

Action-string prefixes, by method count:

`compute` 111 · `node` 26 · `mining` 23 · `txn` 17 · `edge` 16 · `broker` 16 ·
`admin` 15 · `explain` 14 · `memory` 13 · `graph` 10 · `work` 10 · `cdc` 9 ·
`blob` 9 · `lane` 8 · `channel` 8 · `timeseries` 8 · `service` 7 · `matview` 7 ·
`capacity` 7 · `query` 7 · `security` 7 · `resource` 6 · `stream` 6 · `scene` 5 ·
`ingest` 5 · `kv` 5 · `rdf` 4 · `cep` 3 · `reasoning` 3 · `owl` 3 · `ledger` 3 ·
`cluster` 2 · `udf` 2 · `graphlearn` 2 · `sparql` 2 · `validation` 2 ·
`registry` 1 · `federation` 1 · `distcompute` 1 · `jobs` 1 · `statechart` 1 ·
`modality` 1 · `quantum` 1 · `asr` 1 · `viz` 1 · `tts` 1 · `policy` 1

## The 45 actions a bare `kg:read` clears, with method counts

`compute:finance` (67) · `compute:graph-algo` (21) · `compute:datascience` (15) ·
`explain:read` (14) · `node:read` (13) · `edge:read` (12) · `cdc:read` (5) ·
`timeseries:read` (5) · `compute:semantic` (4) · `graph:read` (4) ·
`memory:read` (4) · `blob:read` (3) · `channel:read` (3) · `compute:parse` (3) ·
`ingest:read` (3) · `mining:read` (3) · `owl:read` (3) · `capacity:read` (2) ·
`kv:read` (2) · `lane:read` (2) · `matview:read` (2) · `query:unified` (2) ·
`resource:read` (2) · `scene:read` (2) · `sparql:read` (2) · `stream:read` (2) ·
`txn:read` (2) · `validation:read` (2) · `asr:transcribe` (1) · `cep:read` (1) ·
`cluster:placement-read` (1) · `cluster:topology-read` (1) · `compute:vision` (1) ·
`distcompute:read` (1) · `ledger:read` (1) · `policy:export` (1) ·
`quantum:run` (1) · `query:nl` (1) · `rdf:read` (1) · `reasoning:read` (1) ·
`query:stream` (1) · `tts:synthesize` (1) · `udf:exec` (1) · `viz:render` (1) ·
`work:claim-capability` (1)

**110 of the 221 are `compute:*`** — finance, graph-algo, datascience, semantic,
parse and vision kernels. Whatever else this tier is, it is not "reading rows".

Six of the 221 carry a `#[cfg(feature = ...)]` on their ledger row:

| Method | Action | Feature | In the `default` closure? |
|---|---|---|---|
| `KnowledgeStream` | `query:stream` | `knowledge-batch` | **yes** |
| `Viz` | `viz:render` | `viz` | **yes** |
| `Quantum` | `quantum:run` | `quantum` | no |
| `Asr` | `asr:transcribe` | `asr-native` | no |
| `TtsSynthesize` | `tts:synthesize` | `tts-piper` | no |
| `PolicyExport` | `policy:export` | `policy_export` | no |

`RunUdf` carries **no `cfg` on its ledger row**; its `Method` variant is gated
(`crates/eg-types/src/protocol.rs:2866`, `#[cfg(feature = "wasm-udf")]`) but
`wasm-udf` **is** in the default closure — see §1's finding 2.

## Two definitions of "admin", and the 50 methods between them

| Predicate | Site | Matches | Effect |
|---|---|---|---|
| `coarse_kg_admin_only` | `src/server/auth.rs:632` | `admin:*` prefix, `security:*` prefix, `:admin` suffix, `:control` suffix | A coarse `kg:write` (or `kg:read`) grant is **refused**; an exact scope, a domain wildcard, or `kg:admin` still clears it |
| `is_admin_authz_action` | `src/server/access.rs:1126` | exactly `security:admin`, or an `admin:` prefix | Additionally demands `IsolationLayer::has_admin_capability` — a **pre-registered agent** in `rbac.redb` with an RBAC `Admin` grant, not a token claim |

**22 action strings match the first. Only 5 match the second.** The 17 in the
gap — covering **50 of the 412 methods** — require the `kg:admin` *claim* but no
durable RBAC admin grant:

`blob:admin`, `broker:admin`, `capacity:admin`, `cdc:admin`, `cep:admin`,
`channel:admin`, `federation:admin`, `graph:admin`, `ledger:admin`,
`matview:admin`, `node:admin`, `security:audit`, `service:admin`,
`service:control`, `stream:admin`, `txn:control`, `udf:admin`

The 5 that reach `require_admin_capability` (20 methods): `security:admin`,
`admin:backup`, `admin:cluster`, `admin:cluster-read`, `admin:sqlite-file`.

`security:audit` is the one to watch: it starts with `security:` so
`coarse_kg_admin_only` catches it, but it is not *equal to* `security:admin`, so
`is_admin_authz_action` does not — `AuditVerify` / `AuditProveInclusion` are
claim-gated only. `src/server/policy_export/mod.rs:100-105` is the in-tree
record of this asymmetry, written by the lane that hit it.

## Re-derivation

Every count above comes from this parse of the ledger's own declaration files.
It reimplements `coarse_kg_admin_only`'s four string tests verbatim; run it from
the repository root and it needs no build:

```bash
python3 - <<'PY'
import re, glob, collections
rows = []
for f in sorted(glob.glob('crates/eg-capabilities/src/domains/*.rs')):
    if f.endswith('mod.rs'):
        continue
    cfg = None
    for line in open(f):
        s = line.strip()
        m = re.match(r'#\[cfg\(feature = "([\w-]+)"\)\]', s)
        if m:
            cfg = m.group(1); continue
        m = re.match(r'\("(\w+)",\s*make_policy\((true|false),'
                     r'\s*DurabilityDomain::(\w+),\s*"([^"]+)"', s)
        if m:
            rows.append((m.group(1), m.group(2) == 'true', m.group(4), cfg)); cfg = None
coarse = lambda a: (a.startswith('admin:') or a.startswith('security:')
                    or a.endswith(':admin') or a.endswith(':control'))
admin  = lambda a: a == 'security:admin' or a.startswith('admin:')
ok = [r for r in rows if not r[1] and not coarse(r[2])]
print('MethodPolicy rows           :', len(rows))
print('non-mutating                :', sum(1 for r in rows if not r[1]))
print('reachable by a kg:read scope:', len(ok))
print('distinct actions in that set:', len({r[2] for r in ok}))
print('coarse-admin-only actions   :', len({r[2] for r in rows if coarse(r[2])}))
print('rbac-admin-gated actions    :', len({r[2] for r in rows if admin(r[2])}))
print('methods in the gap          :',
      sum(1 for r in rows if coarse(r[2]) and not admin(r[2])))
PY
```

Expected on `2.27.0`: `412 / 234 / 221 / 45 / 22 / 5 / 50`.

The repository ships its own inventory tool for the same table —
`scripts/method_policy_inventory.py`, which `check_persisted_mutation_contract`
already consumes and which pins `EXPECTED_METHOD_POLICY_ROWS`. Cross-check
against it rather than adding a third counter (parent `SKILL.md` §6, *anti-sprawl pre-flight checklist*).

The feature-closure question ("is this row in a default build?") is answered by
the G3 script in the parent [`SKILL.md`](../SKILL.md) — `133` features,
`97` in the `default` closure, `36` outside it.

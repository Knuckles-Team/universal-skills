# Epistemic-graph architecture reference

Deep reference for `epistemic-graph-development`: the 48-crate component
inventory grouped by layer with what each crate OWNS, the specialty sub-DAGs,
the three crates that already violate the layer numbering, how the
dependency-direction rule is actually enforced (Cargo, not a lint) and where
that guarantee stops, the stale `AGENTS.md` notes, and the placement of the two
`src/` subtrees the layer table used to omit — `src/raft/` and
`src/server/persistence/` — with their measured arch-lint blocker share. The
parent [`SKILL.md`](../SKILL.md) keeps the guardrails, the authorization model,
the anti-sprawl checklist and the workflow; this file is the lookup you open
before creating a crate or moving a module.

## Component inventory — what each crate OWNS

Source of truth: `Cargo.toml` `[workspace] members` (48 entries), each crate's
own `description`, and the dependency edges in their `Cargo.toml` files.

### Layer 0 — contract leaves (zero intra-workspace dependencies)

| Crate | Owns |
|---|---|
| `eg-types` | Wire protocol + graph data model. BOTTOM of the DAG. `protocol.rs` (Request/Response/Method/ResultPayload), `types.rs`, `wire.rs` DTOs, `acl.rs`, **and `mutation_batch/` — the MutationBatch v1 contract itself**. |
| `eg-durable` | Durable-execution ROUTING contracts only (CallShape/WorkShape/DurableBackendKind). No journal, no lease, no 2PC — those live in the crates it routes to. |
| `eg-quantum-core` | QuantumProgram IR, `QuantumBackend` trait + capability flags, estimate()/planner rules R0-R5, exactness-typed `QuantumResult`. Contracts only. |
| `eg-resource` | Dependency-free cgroup-aware resource capacity resolution. |
| `eg-sqlite-format` | Pure-Rust SQLite `.db` file-format reader + bulk-load writer (no C, no libsqlite3). |
| `eg-wasm` | WASM-sandboxed UDF runtime (wasmtime; fuel + memory limits, no host capabilities). |
| `eg-viz-core` | Declarative `ViewSpec` chart IR, `ViewResult` exact-vs-approximated metadata, mark capability matrix, LOD tier-selection rules. |

### Layer 1 — shared seams over `eg-types`

| Crate | Owns |
|---|---|
| `eg-modality` | The `ModalityContract` trait + conformance harness — the seam every modality crate converges on. Deliberately BELOW `eg-plan`/`eg-core` (deps = `eg-types` only). |
| `eg-mutation-store` | The shared redb subordinate-domain ledger for canonical MutationBatch commits: `MutationStore`, `StoreIncarnation`, scope bindings, the batch ledger, private-payload sealing. |
| `eg-capabilities` | Machine-checked `MethodPolicy` capability ledger for the wire protocol. |

### Layer 2 — modality / index leaves over `eg-modality`

| Crate | Owns |
|---|---|
| `eg-audio` / `eg-image` / `eg-video` / `eg-document` | Governed pure-Rust decode + evidence for PCM/WAV, PNG, ISOBMFF+RGB, and typed document pages/layout/tables. |
| `eg-geo` | Geometry, WKT, planar predicates, in-house packed Hilbert R-tree. No GEOS/PROJ. |
| `eg-tensor` | Dense N-D array modality + byte-blob codec. No BLAS. (Also deps `eg-tsdb`.) |
| `eg-text` | Tantivy-backed BM25 inverted index. HARD feature-gated out of the Pi/default build. |
| `eg-stream` | Bounded-NFA complex-event processing over a time-ordered stream. Sync, no tokio. |
| `eg-lake` | LTAP lakehouse interop — Parquet + Delta + Iceberg + Iceberg-REST catalog. A leaf, no workspace edges beyond `eg-modality`. |
| `eg-numeric` | The slim BLAS/LAPACK-free numeric kernel (ndarray + nalgebra). One kernel, two surfaces. |
| `eg-ann` | Native IVF-PQ + OPQ + SQ8-refine ANN index (deps `eg-modality`, `eg-numeric`). |
| `eg-program` | Graph-native governed LM-program and self-improvement contracts. |
| `eg-alignment` | Dependency-light alignment graph + resolver seam over `eg_modality::EvidenceLocus`. |

### Layer 3 — core

| Crate | Owns |
|---|---|
| `eg-core` | `GraphCore` (petgraph graph + ledger), `GraphRegistry` (multi-tenant), `isolation.rs` (zero-trust ACL, `mint_graph_policy_lease`), `SemanticStore`, `rls_view_cache.rs`, `rbac_persist.rs`. Deps: `eg-ann`, `eg-modality`, `eg-mutation-store`, `eg-types`. |

### Layer 4 — storage / transaction

| Crate | Owns |
|---|---|
| `eg-tsdb` | Native time-series store + TS primitives (time_bucket/ASOF/gap-fill/OHLC/rollup). Owns its own native mutation scope. |
| `eg-jobs` | Durable analytics-job plane over a redb-backed `AnalyticsJob` state machine; commits results as provenance'd claims. |
| `eg-statechart` | Formal FSM/statechart engine + durable redb machine-instance store. The disciplined sibling of `eg-jobs`' job primitive. |
| `eg-kvcache` | Tiered hot/warm/cold KV-cache store + content-addressed shared multi-instance backend. |

### Layer 5 — query / reasoning

| Crate | Owns |
|---|---|
| `eg-compute` | Compute domains: graph algorithms (always compiled), AST/tree-sitter, finance, datascience, Datalog reasoning. |
| `eg-query` | SQL/Cypher surface (DataFusion behind the `sql` feature); the SQL catalog and its native scope key. |
| `eg-epistemic` | Claims, evidence, belief-state, contradiction, confidence propagation, justification (TMS). |
| `eg-plan` | THE unified cross-modal planner: a RowSet closed algebra sequencing SQL, graph and vector legs into one plan with cost-based reorder. Widest fan-in in the workspace (13 path deps). |
| `eg-rdf` | RDF ↔ property-graph mapping + SPARQL 1.1 compiled to GraphView scans. |
| `eg-shacl` / `eg-shex` | Pure-Rust SHACL Core / ShEx Core validation over `eg-rdf`'s oxrdf model. |
| `eg-graphql` | Native GraphQL read surface: schema-from-graph + resolver compiling to GraphView scans. |

### Layer 6 — server / protocol adapter (the root facade, NOT a crate)

There is deliberately **no `eg-server` crate**. `src/` is the `epistemic-graph`
facade at the TOP of the DAG: `src/server/` (66 entries) holds `dispatch.rs`,
`handlers/`, `state.rs`, `auth.rs`, `access.rs`, `transport.rs`, `mutation.rs`,
`mutation_batch.rs`, `persistence/`, the wire family (`pgwire`, `mysql_wire`,
`mssql_wire`, `bolt_wire`, `redis_wire`, `sqlite_wire`, `amqp_wire`, `mqtt_wire`,
`stomp_wire`, `broker_wire`), `federation/`, `cdc*`, `s3/`, `lake/`, `obda/`.
Rationale (`AGENTS.md`): the server lib and the bin are 1:1, so splitting a crate
would carry no consumer and entangle the `server`/`metrics` features.

### Layer 7 — binary composition

`[[bin]]` targets in the root `Cargo.toml`, each behind `required-features`:
`epistemic-graph-server` (`server`), `nemesis` (`harness`), `migrate-shards`
(`redb, server`), `restore` (`redb, server`), `lake-fixture-export` (`lake`). Feature
selection and process lifecycle only.

### Specialty stacks (own sub-DAGs, default-off)

- **Quantum (6):** `eg-quantum-core` (contracts) → `eg-quantum-gates` (unitary
  matrices) → `eg-quantum-sim` (statevector + stabilizer) ; `eg-quantum-hardware`
  (IBM/Braket/Azure adapters, always `BackendFamily::Hardware`, never exact);
  `eg-quantum-jobs` (quantum as an `eg-jobs` AnalyticsJob); `eg-quantum-workloads`
  (QAOA writing back TYPED PROPOSALS through the `:Claim`/`:Evidence`/`SUPPORTS`
  convention, never a hard constraint).
- **Viz (5):** `eg-viz-core` (contracts) → `eg-viz-columnstore`, `eg-viz-kernels`
  (M4/LTTB, runtime-detected AVX2), `eg-viz-graph-tiles`, `eg-viz-export`.
- **Providers (2):** `eg-asr-whisper` (implements `eg-audio`'s frozen `asr.*`),
  `eg-tts-piper` (implements the `tts.*` contract).
- **Embedding (1):** `eg-pyengine` — in-process PyO3 binding. Opt-in only; the
  out-of-process build must never link it (`scripts/check_no_pyo3.sh`).

### The dependency-direction rule

> **A crate may only `use` crates to its left. No storage or query crate imports
> server dispatch.**

⚠ **The layer numbering above is a target, not a description — three existing crates
violate it, so do not use the table to answer "is this edge legal?".** Verified from
the manifests: `eg-tsdb` (L4) depends on `eg-compute` (L5); `eg-kvcache` (L4) depends on
`eg-compute` (L5); `eg-tensor` (L2) depends on `eg-tsdb` (L4). The invariant that
actually holds today is the narrow one — **nothing under `crates/` depends on the root
`epistemic-graph` facade** — plus the direction of travel: a new edge should go
*downward* in this table, and an upward one needs a stated reason, not a shrug that
three others already exist.

**How it is enforced — by Cargo, not by a lint.** No hook checks crate-graph
direction (`rust-arch-lint` has no such rule — see the parent `SKILL.md` §3 and [`gates-reference.md`](gates-reference.md)). Cargo does the work: `crates/*`
cannot depend on the root `epistemic-graph` package because the root depends on them.
Verified: **no `crates/*/Cargo.toml` declares `epistemic-graph` in `[dependencies]` or
`[dev-dependencies]`.** A `[dependencies]` cycle simply will not build. That is stronger
than any gate, and it is why "put it in the server" is the sprawl-safe default only when
the thing genuinely has no reusable core.

> ⚠ **The guarantee covers `[dependencies]` only.** Cargo permits cycles through
> `[dev-dependencies]`, and this workspace has them. `eg-modality` — the Layer-1 seam
> every modality crate sits on — dev-depends on `eg-audio`, `eg-document`, `eg-geo`,
> `eg-image`, `eg-tensor`, `eg-video`, and **all six depend on `eg-modality`**. (Also:
> `eg-viz-core`, listed as a zero-dependency Layer-0 leaf, dev-depends on `eg-jobs` —
> not a cycle, but not a leaf either.) So "a cycle will not build" is true of the
> shipped graph and **false** of the test graph. Do not add a dev-dep downward and
> assume the compiler will stop you.

Corollary rules from `AGENTS.md` ("Workspace & server dispatch conventions"):

- A new shared/wire type → `eg-types`. A new graph-core capability → `eg-core`.
  A new compute domain → `eg-compute`.
- **Wire DTOs live in `eg-types`, behavior lives upstream.** Never pull nalgebra
  or tree-sitter into a default build to satisfy a type — feature-gate it.
- **Dispatch is a thin routing table.** A routing arm must contain no business
  logic; logic lives in `handlers::<domain>`. Post-match write side-effects
  (in-flight gauge, redb commit, CDC emit) stay centralized in the shell.
- **One handler module per domain**, 1:1 with the `// -- <domain> --` sections in
  `protocol.rs`. A new domain gets a new `handlers/<domain>.rs`, never another arm.
- **Feature-gating gates three sites:** crate/feature wiring, the handler `mod`,
  and the dispatch routing. A gated-out `Method` variant stays in the enum and
  falls to the explicit "not available in this server build" catch-all — never a
  panic, never a silent mis-route.

> ⚠ **Known contradiction, current tree:** `src/server/dispatch.rs` is
> **14,174 lines**. The "thin routing table" convention describes the intent, not
> the present state. Do not read the convention as a description of what you will
> find; read it as the direction any change must move.

> ⚠ **`AGENTS.md`'s "Module Structure" ASCII tree is STALE.** It documents a
> 5-crate DAG (`eg-types → eg-ann → eg-core → eg-compute → epistemic-graph`). The
> workspace has 48 crates. Use `Cargo.toml` `[workspace] members` and the table
> above; treat that tree as historical.

### Where `src/raft/` and `src/server/persistence/` sit

The Layer-6 entry above enumerates `src/server/`'s contents. Two large `src/`
subtrees need their own placement, because neither is a "protocol adapter" and
one of them is not under `src/server/` at all.

| Subtree | Measured size | Layer | Gate posture |
|---|---|---|---|
| `src/server/persistence/` | **21,637 lines in 13 files** (`find src/server/persistence -name '*.rs' \| xargs cat \| wc -l`) — `mod.rs` (the `GraphStore` trait), `redb_backend.rs` (9,829 lines, the ONE served implementation), `backup.rs`, `shard_migrate.rs`, `online_reshard.rs`, `rebalance.rs`, `cold_offload.rs`, `read_through.rs`, `durable_stores.rs`, `tenant_catalog.rs`, `node_info_store.rs`, `cluster_hierarchy_store.rs`, `provenance_anchor.rs` | **Layer 4 content living inside the Layer-6 facade.** It is the authoritative durable graph-store contract + backend, not a wire adapter: its own module doc says *"The served engine has one implementation, `redb_backend::RedbBackend`. The trait keeps mutation, recovery, read-through, backup, and Raft consumers on one contract without exposing storage internals."* It is under `src/server/` for the same reason there is no `eg-server` crate (1:1 lib/bin, entangled `server`/`metrics` features), NOT because it is protocol code. Treat a new storage capability as Layer-4 work even though the file lives at `src/server/persistence/`. | In the DEFAULT build (`redb` is in `full` ⊂ `default`), so clippy and `--lib` cover it. |
| `src/raft/` | **29,761 lines in 32 files** (`find src/raft -name '*.rs' \| xargs cat \| wc -l`) — `node.rs`, `store.rs`, `network.rs`, `membership_shrink.rs`, `reshard.rs`, `placement.rs`, `cross_shard_txn.rs`, `cross_node_elasticity.rs`, `pregel.rs`, `xread.rs`, `exchange.rs`, `drain.rs`, `multi.rs`, `config.rs`, plus 6 `*_harness*.rs` and `tests.rs` | **A replication/consensus tier BESIDE the server adapter, not inside it.** It is a top-level `src/` module (`src/raft/`, one of only five `src/` subdirectories — `bin/`, `embedded/`, `raft/`, `redb_store/`, `server/`), declared at `src/lib.rs:154`. Its own module doc: *"Runs the engine as a multi-node, highly-available cluster that replicates its AUTHORITATIVE state through `openraft`."* It consumes the storage layer (`src/raft/cross_shard_txn.rs:845` calls `eg_mutation_store::read_record`) and is consumed by dispatch through `#[cfg(feature = "raft")]` arms — so in dependency terms it sits **between** Layer 4/5 and the Layer-6 dispatch shell. | **Outside the default build.** `src/lib.rs:150-154` gates `pub mod raft;` on the `raft` feature, reachable only through `cluster`, which is not in `default` — see G3 in the parent `SKILL.md`. Nothing in the routine gate suite type-checks it. |

**Why the placement matters for effort, not just tidiness.** Re-measured
2026-09-04 with `arch-lint check --format json` at the repo root, bucketing
`violations[].location.file` by path prefix in Python:

| Bucket | AL002 blocking errors | All severities |
|---|---:|---:|
| `src/server/persistence/` | **203** | 307 |
| `src/server/` (other) | 153 | 1,160 |
| `src/` (other, incl. `src/redb_store.rs`) | 112 | 362 |
| `crates/` | 92 | 1,411 |
| `src/raft/` | **90** | 217 |
| `tests/` | 29 | 29 |
| `benches/` | 6 | 6 |
| `examples/` | 2 | 6 |
| `target-isolated/` (build artifacts) | 0 | 858 |
| other `target-*/` (build artifacts) | 0 | 286 |
| **Total** | **687** | **4,642** |

So `src/raft/` + `src/server/persistence/` hold **293 of the 687** blocking
errors — **42.6%**, in **45 of 1,077** scanned files. A prior measurement in
this program recorded **375 of 687** for the same two directories; **293 is the
number this skill stands behind**, because it is reproducible from the command
above and the bucketing rule is stated. If your own count differs, publish the
bucketing rule with it (**G1**, **G10**) — "375" and "293" are not both wrong,
they are answers to two differently-drawn universes.

The concentration is four files: `src/server/persistence/redb_backend.rs` (97),
`src/redb_store.rs` (49), `src/server/persistence/shard_migrate.rs` (40),
`src/raft/tests.rs` (37). Every one of the 687 is AL002 `no-sync-io` — a
storage/consensus tier calling `std::fs` on an async runtime — which is exactly
what you would predict from the placement above, and is the reason "burn down
arch-lint" is a **storage** workstream, not a server one.

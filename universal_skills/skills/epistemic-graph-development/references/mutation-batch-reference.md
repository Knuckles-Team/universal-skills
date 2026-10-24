# MutationBatch v1 contract reference

Deep reference for `epistemic-graph-development`: the full MutationBatch v1
contract — scope and domain as two independent axes, the three domain classes
with the validator's exact accept/reject table, the three `const fn` predicates
and the different question each one answers, the store-plus-identity consumer
shape with the worked `rbac_persist.rs` reference implementation and its commit
sequence, the `.database()` chokepoint failure with all 17 bypassing production
call sites, and the recorded miswrites. The parent
[`SKILL.md`](../SKILL.md) keeps the guardrails, the authorization model, the
anti-sprawl checklist and the two-line summary of this contract; open this file
before you compile, commit, or validate a batch, or before you give a store its
`MutationScopeIdentity`.

## The MutationBatch v1 contract

**Authority:** `crates/eg-types/src/mutation_batch/` — `model/request.rs`
(`MutationDomain` + its three predicates), `model/identity.rs`
(`MutationScope`, `MutationScopeIdentity`, `PRIVATE_PAYLOAD_EVENT_TYPES`,
`COMPILED_BATCH_INCARNATION`), `validation.rs` (`validate_operations`).
Ledger: `crates/eg-mutation-store/`.

### Scope and domain are TWO INDEPENDENT AXES

- **Domain** (`MutationDomain`, 14 variants) names the **operation family**.
- **Scope** (`MutationScope::Graph { graph } | Native { domain, resource }`) names
  the **storage authority** — which store owns the state and its version counter.

Conflating them is what made every control-plane batch unrepresentable: a graph
scope was rejected by `validate_operations`, and a native scope was rejected one
call deeper by the graph commit route (`mutation_batch_graph_name` in
`src/redb_store.rs` fails closed on anything but `MutationScope::Graph`; the only
OCC counter is `MUTATION_GRAPH_VERSION`, keyed by graph name).

### Three domain classes

The table below states what the **validator** accepts. `validate_operations`
(`validation.rs:133`) rejects a graph scope for exactly the domains matched by
`forbidden_in_graph_scope()` (`request.rs:129`), and a native scope whose declared
domain differs from the operation's.

| Class | Domains | Graph scope | Native scope |
|---|---|---|---|
| **graph-only** | `GraphRows`, `GraphSnapshot`, `RdfDataset` | yes | no (`may_own_native_scope` is false) |
| **store-only** | `BlobStore`, `KvStore`, `TimeSeries`, `AnalyticsJob`, `SemanticIndex` | no | yes, domain must match |
| **either** | `Lifecycle`, `ControlPlane`, `CrossModal`, `MultiGraph`, **`SqlCatalog`, `Broker`** | yes | yes |

`SqlCatalog` and `Broker` are **legal in a graph scope** — they are absent from
`forbidden_in_graph_scope`. They sit in the "either" class even though the *producer*
defaults them to native (`requires_native_scope`); that split is the whole point of the
two predicates below, and it is why a domain's legal scopes must never be read off the
producer's default.

"Either" is load-bearing **both ways**: a `ControlPlane` WorkItem CAS rides the
graph OCC counter, while the RBAC `security-control` store is a `ControlPlane`
**native** scope with its own counter.

### Three predicates — each answers a DIFFERENT question

All three are `const fn` on `MutationDomain` in
`crates/eg-types/src/mutation_batch/model/request.rs`:

| Predicate | Line | Question | Consumer |
|---|---|---|---|
| `may_own_native_scope()` | 101 | "May this domain own a native scope?" — `!(GraphRows \| GraphSnapshot \| RdfDataset)` | `MutationScope::validate` (`model/identity.rs`) |
| `forbidden_in_graph_scope()` | 129 | "May this domain NEVER ride a graph scope?" — `BlobStore \| KvStore \| TimeSeries \| AnalyticsJob \| SemanticIndex` | the **validator** |
| `requires_native_scope()` | 140 | "What scope should a compiled batch default to?" — the `forbidden_in_graph_scope` set **plus `SqlCatalog` and `Broker`** | the **producer** default in `src/server/mutation_batch.rs`: `graph_scope = !domain.requires_native_scope()` |

`SqlCatalog` and `Broker` are exactly where the validator's and producer's answers
diverge: both default to native (eg-query's `sql_scope_key`; the broker's own
compile sites) yet both also travel legitimately through the graph kernel — a wire
`INSERT INTO nodes` really is a graph-row mutation written in SQL, and `Broker`
owns no mutation store at all.

> **Do not collapse these.** It was tried and measurably regressed the suite
> **15 → 27 failures** (12 previously green `wired_catalog_tests`/`sqlite_wire`
> tests went red).
>
> ⚠ **The inline `NOTE:` at `request.rs:140` is a STALE source comment.** It says
> `requires_native_scope` "is doing DOUBLE DUTY", answering both the validator's and
> the producer's question. That is no longer true: its only call sites in the tree are
> `src/server/mutation_batch.rs:137` and `:178`, **both producer-side**
> (`graph_scope = !domain.requires_native_scope()`); the validator calls
> `forbidden_in_graph_scope` and `MutationScope::validate` calls
> `may_own_native_scope`. Everything else that mentions it is a doc comment.
>
> What **is** still open (D-4, narrowed) is smaller: the producer derives the scope
> from the **domain tag** rather than from the commit route. The fix is at the
> graph-routed callers: **choose the scope explicitly. Scope is a property of the
> commit ROUTE, which only the caller knows — never derive it from the
> operation-family tag.**

### Every consumer holds a store + an identity, never a bare `Database`

```rust
pub struct RbacStore {
    mutation_store: eg_mutation_store::MutationStore,
    identity: eg_types::MutationScopeIdentity,
}
```

`MutationStore` (`crates/eg-mutation-store/src/store/identity.rs:127`) holds
`database`, `handle`, `physical_path`, `private_integrity` as private **fields**.
`MutationStore::write() -> MutationWrite` (`:150`) is the **intended** mint path: it
calls `validate_physical_root()`, sets `Durability::Immediate`, and then
`validate_handle_write(&self.handle, &transaction)` before handing back a
`MutationWrite`.

> ⚠ **It is not a chokepoint.** `pub fn database(&self) -> &Database` at
> `identity.rs:142` hands out the raw redb handle, and **17 production sites call
> `.database().begin_write()`**, skipping `validate_physical_root` and
> `validate_handle_write` entirely: `src/server/kv.rs:193,218,328`;
> `src/server/blob/store.rs:570,643,699,1315`; `crates/eg-jobs/src/store.rs:1241,1297,1362`;
> `crates/eg-statechart/src/store.rs:267`; `crates/eg-tsdb/src/store.rs:562,582,774,812,934,977`
> (plus `crates/eg-mutation-store/src/store/recovery.rs:131` inside the owning crate,
> and test-only sites in `rbac_persist.rs`, `eg-tsdb`, `store/tests.rs`). 71
> `.database()` call sites exist in total. This is the parent `SKILL.md` §6's *"enforce at the chokepoint,
> not one entrypoint"* checklist item failing in this very repo: a control wired into
> one constructor while a public accessor next to it lets every caller around it.
> **Write through `write()`.** If you genuinely need the raw `Database`, say why at
> the call site — and do not read the existence of `write()` as proof the invariant
> holds.

**Worked reference — `crates/eg-core/src/rbac_persist.rs`:**

```rust
const RBAC_SCOPE_TENANT: &str = "native";
const RBAC_SCOPE_RESOURCE: &str = "security-control";
const RBAC_SCOPE_INCARNATION: &str = "rbac-security-control:v1"; // NOT derived from the resource name

fn native_security_control_identity() -> Result<eg_types::MutationScopeIdentity, RbacPersistError> {
    eg_types::MutationScopeIdentity::fixed_native(
        RBAC_SCOPE_TENANT,
        eg_types::mutation_batch::MutationDomain::ControlPlane,
        RBAC_SCOPE_RESOURCE,
        RBAC_SCOPE_INCARNATION,
    ).map_err(RbacPersistError::Redb)
}

pub fn open<P: AsRef<Path>>(dir: P) -> Result<Self, RbacPersistError> {
    let identity = native_security_control_identity()?;
    let mutation_store = eg_mutation_store::initialize(&path, &identity, 0, None, |wtx| {
        wtx.open_table(RBAC_TABLE).map_err(|e| e.to_string())?;
        Ok(())
    }).map_err(RbacPersistError::Redb)?;
    let store = Self { mutation_store, identity };
    store.bootstrap_current_state()?;
    Ok(store)
}
```

Commit sequence on the write path:
`version(&store, &identity)` → set `VersionExpectation::Native(expected)` →
`store.write()?` → `begin(&write, &batch)?` → on `Begin::Replay(_)` **return early
without committing** (redb's `Drop for WriteTransaction` aborts) → on
`Begin::Apply { source_version }` write rows via `write.owner_rows().open_table(...)`
→ `finish(&write, &batch, Some(payload), 0, source_version)?` → `commit(write, &batch)?`.

**Rules that fall out:**

- The identity's `MutationDomain` must equal every `MutationOperation::domain` the
  store writes — the native-scope validator requires exact equality.
- A per-store **incarnation is a fixed literal**, not derived from the resource
  name, because the scope is never deleted and recreated for the life of one
  physical file; `bind_scope_in`'s idempotent-rebind check fails closed otherwise.
- For a `CompileBatch`, the `resource` string must be **exactly** the string passed
  as `CompileBatch::graph`, with the same domain and the same
  `eg_types::mutation_batch::COMPILED_BATCH_INCARNATION`. Any one of the three
  drifting fails every write on that scope closed.
- Free functions on the store: `initialize`, `bind_scope`, `version`, `read_record`,
  `begin`, `finish`, `commit`, `purge_scope`, `adopt_restored_store`,
  `adopt_restored_store_if_mutation_store`.

> **Common miswrite:** `identity.graph_name()`. `MutationScopeIdentity` has **no**
> `graph_name()` — it is on `MutationScope`
> (`crates/eg-types/src/mutation_batch/model/identity.rs:105`, returning
> `Option<&LogicalName>`: `Some` for `Graph`, `None` for `Native`). The correct chain is
> `identity.scope().graph_name()`. Related: `MutationVersionScope` and
> `NON_GRAPH_SOURCE_VERSION` are genuinely gone from the tree — the only remaining
> mention is an explanatory comment at `crates/eg-types/src/lib.rs:146`.

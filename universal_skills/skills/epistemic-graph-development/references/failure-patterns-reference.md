# Epistemic-graph failure-pattern reference

Deep reference for `epistemic-graph-development`: the seven documented EG
failure patterns in full — each with the source-tree `file:line` evidence
re-verified against the current tree, and the rule it was promoted into. The
parent [`SKILL.md`](../SKILL.md) carries the rule statements and the index of
these patterns; open this file when you need the evidence behind one, or when a
recorded finding looks authoritative and you are about to act on it (**G6**).
Section numbering matches the parent's index.

## Documented failure patterns — stated as rules

Each rule below is grounded in the cited source paths. Recheck paths and
observed behavior against the current public checkout before acting on it.

### 7.1 A predicate consulted by both a validator and a producer is answering two questions

*Evidence:* `BLOCKER-V1-SCOPE-DOMAIN-CONTRADICTION-20260903.md`;
`DUPLICATION-AND-SPRAWL-INVENTORY-20260903.md` items B-3, B-5, D-4.
`MutationDomain::is_native_scope_domain` served `MutationScope::validate` AND
`validate_operations`. The first "fix" — a two-class partition — compiled and
passed its own new fixture, then failed a **pre-existing** test with
`"mutation domain 'control_plane' cannot own a native scope"`. The same shape
recurred three times in one session (B-3, B-5, D-4).

> **Rule:** before reusing a predicate, name its caller and the exact question that
> caller is asking. Two callers means two questions until proven identical. A
> plausible fix that compiles and passes its own new fixture can still be wrong;
> only the pre-existing suite catches this class.

### 7.2 A hand-copied list of another crate's tables/events cannot stay correct

*Evidence:* `V1-PRIVATE-PAYLOAD-GATE-REGRESSION-20260903.md`; inventory B-1, B-2.
Producers declared their own event families in `src/server/dispatch.rs`
(`SPARQL_RECOVERY_EVENT`, `SPARQL_COMPENSATION_EVENT`) and
`src/server/handlers/txn.rs`, while the scan hard-coded
`"transaction_recovery_plan"` inside `eg-mutation-store`. A set declared in one
crate cannot be seen by the other. Also: `COMPILED_BATCH_INCARNATION` was
duplicated across `src/server/mutation_batch.rs` and `crates/eg-tsdb/src/store.rs`.

> **Rule:** when a scan in crate A must know a set produced in crate B, the set
> moves to a crate both can import. Today that is
> `eg_types::mutation_batch::PRIVATE_PAYLOAD_EVENT_TYPES` and
> `eg_types::mutation_batch::COMPILED_BATCH_INCARNATION` — both now verified in
> `crates/eg-types/src/mutation_batch/model/identity.rs`.

### 7.3 Extracting a shared helper silently ADDS a control to paths that never had one — or REMOVES one

**Added:** the private-payload gate. On main, `"transaction_recovery_plan"`
appeared twice, both inside `validate_recovery_store` — a backup scan, on no
production path. The v1 candidate extracted `recovery_plan_digest` and wired it
into three hot paths (`ledger.rs::persist_private`,
`ledger.rs::read_private_in_write`, `persist.rs::read_private_payload`) alongside
the one legitimate scan. Every SPARQL-HTTP update saga then failed with
`"private recovery payload has no digest-bound parent"` on seal-write and every
read after. Fixed by splitting `private_payload_digest` (hot path, no `event_type`
inspection) from `recovery_plan_digest` (scan only, filtered by the declared set) —
both verified in `crates/eg-mutation-store/src/store/ledger.rs:202` and `:227`.

**Removed:** the RLS view cache. `crates/eg-core/src/rls_view_cache.rs` defines
`FilteredViewCache: HashMap<String, (u64, Arc<GraphView>)>` keyed by **actor string
+ graph-content version only** — no policy, role, grant, or identity digest. On a
hit, `rls.filter_view` is **never called**. `invalidate_filtered_view_cache` is
invoked from exactly two whole-image graph transitions
(`crates/eg-core/src/graph.rs:6183` and `:6253`). The permission mutators in
`crates/eg-core/src/isolation.rs` — `try_add_grant`, `try_remove_grant`,
`try_register_agent` — contain **zero** invalidation calls. Revoke a grant and the
actor keeps being served rows the current policy forbids.

> **Status re-verified on the current tree: STILL OPEN.** `grep -c
> invalidate_filtered_view_cache crates/eg-core/src/isolation.rs` = **0**, and the
> cache is consulted from 6 read sites: `src/server/access.rs:301`,
> `src/server/handlers/rdf.rs:131/162/462`, `src/server/handlers/query.rs:5627/5684`.
> (The report's `query.rs:5332/5390` line numbers have shifted.) Any fix must
> either key the cache on a policy/identity digest, invalidate from every
> RBAC/identity mutation, or remove the cache — its own doc says a miss "costs
> exactly what every call cost before this cache existed."

> **Rule:** an extraction changes the *set of call sites* a control runs on. Before
> extracting, enumerate the paths that did not have the control. After extracting,
> enumerate them again. A performance optimization that skips a filter is a
> security change, and no gate in this repo observes it.

### 7.4 Binding identity to a physical path breaks legitimate relocation

*Evidence:* `SEC-FINDING-V1-INCARNATION-BREAKS-RESTORE-20260903.md`.
`StoreIncarnation::derive` (`crates/eg-mutation-store/src/store/identity.rs:65`,
`pub(crate)`) canonicalizes the path and calls `physical_root_id` (`:765`), which
hashes `PHYSICAL_ROOT_DOMAIN` + `metadata.dev()` + `metadata.ino()` — **and nothing
else**. `initialize` re-derives on every open and fails closed on mismatch. Correct
for detecting live-file substitution; unavoidably false for a restored backup (new
file, new inode) — so *reading a published bundle at all* was broken, before
`restore_bundle` even reached `fs::copy`. Copying `STORE_ROOT`/`SCOPE_BINDINGS`
made reopen fail on incarnation mismatch; omitting them made it fail with
"mutation version row exists without a scope binding". Only an empty store survived
either way, which is why it was not caught earlier. Blocks `RELEASE-CUTOVER-CONTRACT.md`
RC-08 and is a prerequisite for PA-01.

Resolution shape landed as `adopt_restored_store` and
`adopt_restored_store_if_mutation_store` (verified at `identity.rs:327` and `:305`),
applied **once at the restore boundary inside `restore_bundle`** rather than teaching
six store owners a restore mode.

> **Read the current code, not the finding.** An earlier revision *did* also hash the
> canonicalized path string; that was removed by the fix. `physical_root_id` now
> carries a verbatim `NOTE:` (`identity.rs:754-761`) saying it deliberately does **not**
> hash `path`. The practical consequence: a same-filesystem `rename` (staging dir →
> published location) preserves `(dev, ino)` and therefore **does not** change the
> incarnation. Only a **copy** does — which is exactly the restore case
> `adopt_restored_store` exists for.

> **Rule:** identity derived from a physical location cannot distinguish
> substitution from relocation. Give relocation an explicit, invariant-checking
> adoption entry point and put it at the one boundary that knows a relocation is
> happening — never at each of the N owners.

*Companion, same report:* `prepare_saga_with_private_payload` / `commit_saga` /
`read_private_payload` hard-fail when the store was constructed with `None` for
`PrivatePayloadIntegrity`. A mechanical migration produces `None`, which compiles.
> **Rule:** nothing in the type system distinguishes "no private payloads" from
> "unauthenticated private payloads." `None` on a security seam needs a named
> reason at the construction site.

### 7.5 A fix that passes only the test its author wrote has demonstrated almost nothing

*Evidence:* the two-class predicate partition (7.1) passed its new fixture and broke
a pre-existing one. The 15 → 27 regression ([`mutation-batch-reference.md`](mutation-batch-reference.md)) was found only by the full suite.
`SEC-FINDING-V1-INCARNATION-BREAKS-RESTORE` notes an existing regression at
`src/server/persistence/backup.rs:1470` that *should* start failing once the tree
builds — evidence the suite already encoded the invariant nobody re-read.

> **Rule:** run the pre-existing suite, and say which pre-existing test would have
> caught the bug had it been running. If none would have, you have not written the
> test yet. Corollary (`GOC-70`): a test that only passes on a large machine is a
> defective test — assert that the operation *landed*, never that N tasks
> overlapped; construct contention deterministically (barrier/lock/synchronous
> enqueue), never by spawning N tasks and hoping.

### 7.6 Two more that cost time — orchestration, not code

- **A named reference implementation is a copy instruction.** The migration named
  `rbac_persist.rs` as the exemplar without giving the pattern a shared home, and
  **eight** near-identical scope-identity builders appeared. Extract the shared
  primitive BEFORE fan-out, not after. (Partially collapsed today:
  `MutationScopeIdentity::fixed_native`/`fixed_graph` now back `rbac_persist.rs:64`,
  `eg-jobs/src/store.rs:2382`, `eg-statechart/src/store.rs:738`, and
  `src/server/persistence/redb_backend.rs:1347`; `src/server/blob/store.rs:454`
  still hand-rolls the four-constructor form.)
- **File-partitioned lanes prevent edit collisions, not pattern collisions.**
- **Never park a lane on a background watcher.** Tell it to re-run the command and
  verify directly; two lanes waited for a notification that never fired.

### 7.7 Known open items to check before you assume something is broken

| Item | State |
|---|---|
| D-4 `requires_native_scope` double duty | **Stale as written.** The predicate no longer serves the validator — its only call sites are `src/server/mutation_batch.rs:137` and `:178`, both producer-side; the `NOTE:` at `request.rs:140` is an out-of-date source comment. What remains open is narrower: the producer derives scope from the domain tag, not the commit route. Fix belongs at the graph-routed callers. |
| RLS view-cache staleness | **Open on the current tree** (verified §7.3 below). |
| C-1 the `security` feature is a second architecture | Verified today: **636** `cfg(feature = "security")` arms vs **64** `cfg(not(feature = "security"))` arms across `src/` and `crates/`. `security` is in `full`, which is `default`, so the negative arms are an alternate, unauthenticated implementation reachable only via `--no-default-features`. Deferred; proposal in `evidence/proposals/EG-SECURITY-DEGATING-SLICE.md`. |
| D-3 `txn.rs:683` compares a tenant against a graph name | Real pre-existing bug; fix needs the tenant threaded through `ReconcileTxnCandidate`. |
| D-2 three `private_interfaces` warnings in `eg-mutation-store` | `StoreHandle` is more private than `initialize_in`/`bind_scope_in`/`validate_handle_write`. Pre-existing. |

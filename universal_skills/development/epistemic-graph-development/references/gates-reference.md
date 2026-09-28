# Epistemic-graph gate reference

Deep reference for `epistemic-graph-development`: every architecture-,
contract- and hygiene-enforcing hook `.pre-commit-config.yaml` declares, the
script behind it and exactly what it refuses; which non-Rust hooks have a
scope that is routinely misread; the per-hook measured PASS/FAIL state on the
current tree with each failure's actual message; and the `rust-arch-lint`
denominator with its build-artifact contamination broken out. The parent
[`SKILL.md`](../SKILL.md) keeps the guardrails, the authorization model, the
gate-authoring rules and the workflow. Per **G2**, read the row here — and the
gate script's own docstring — before citing what a gate enforces; a
`.pre-commit-config.yaml` comment is not the gate's behaviour, and neither is
`arch-lint.toml`.

## Invariants that are actually enforced, and by what

`.pre-commit-config.yaml` declares **60 hooks**. These are the architecture- and
contract-enforcing ones. Every script path below was verified to exist.

### Rust / architecture

| Hook id | Runs | Forbids |
|---|---|---|
| `rust-arch-lint` | `arch-lint check --format json`, config `arch-lint.toml` | **Not** dependency direction — `arch-lint` 0.5.0 has exactly 8 rules and none of them checks crate-graph direction: AL001 `no-unwrap-expect`, AL002 `no-sync-io`, AL003 `no-error-swallowing`, AL004 `handler-complexity`, AL005 `require-thiserror`, AL006 `require-tracing`, AL007 `tracing-env-init`, AL013 `no-silent-result-drop` (`arch-lint list-rules`). The DAG is enforced by Cargo (parent `SKILL.md` §2, and [`architecture-reference.md`](architecture-reference.md)). `arch-lint.toml` sets `preset = "minimal"` and `[rules.no-unwrap-expect] enabled = false`; **0.5.0 does not honour the preset** — it logs `Analyzing "." with 7 rules` and runs every rule except the explicitly disabled AL001. |
| `check-crates-io-only` | `scripts/check_crates_io_only.py` | Any `git = "..."` dependency source; any `path = "..."` resolving OUTSIDE this workspace. Covers **49** manifests — the root `Cargo.toml` plus all 48 `crates/*/Cargo.toml` — and `Cargo.lock`. |
| `cargo-deny-advisories` | `scripts/check_cargo_advisories.sh` | Known-CVE Rust dependencies. |
| `cargo-clippy` | `cargo clippy --no-default-features --features full --all-targets -- -D warnings` | Any warning in the shipped `full` build. |
| `cargo-clippy-all-features` | `scripts/check_cluster_extras_affected_lint.py` | Same, `--all-features`, scoped to affected crates. HEAVY / pre-push. |

### Persistence + mutation contract

| Hook id | Script | Forbids |
|---|---|---|
| `persisted-mutation-contract` | `scripts/check_persisted_mutation_contract.py` | Regression of current-only mutation/projection persistence. Now sources its inventory from `scripts/method_policy_inventory.py`. |
| `current-only-architecture` | `scripts/check_current_only_architecture.py` | Return of audited legacy readers or execution fallbacks. |
| `lazy-lifecycle-architecture` | `scripts/check_lazy_lifecycle_architecture.py` | Unbounded / generation-unsafe lazy graph lifecycle. |
| `canonical-property-schema` | `scripts/check_canonical_property_schema.py` | Reinterpreting a user payload field named `type` as an edge relationship or KnowledgeSet row kind; restoring the former `rel_type` integration key. |
| `exact-fault-restart-harness-architecture` | `scripts/check_exact_fault_restart_harness.py` | Drift in the exact-binary fault/restart certification architecture. |

### Security / isolation

| Hook id | Script | Forbids |
|---|---|---|
| `universal-read-rls-architecture` | `scripts/check_universal_read_rls.py` | A served read bypassing row or carrier ownership isolation. Unauthenticated HTTP/SSE/bridge carriers must fail closed. |
| `mint-lease-call-sites` | `scripts/check_mint_lease_call_sites.py` | A **second** production call site for `IsolationLayer::mint_graph_policy_lease`. The one permitted caller is `authorize_and_route_knowledge_stream` in `src/server/dispatch.rs`. |
| `guardrail-tracked-privacy` | `scripts/check_tracked_privacy.py` | Host-specific data or local identities in tracked public artifacts. |
| `security-sanitizer` | `scripts/security_sanitizer.py` | Security/garbage patterns. |

### Protocol / domain architecture

| Hook id | Script | Forbids |
|---|---|---|
| `p2-modality-architecture` | `scripts/check_p2_modality_architecture.py` | Bypassing the P2 modality/KnowledgeBatch architecture. |
| `p2-analytics-reasoning-architecture` | `scripts/check_p2_analytics_reasoning_architecture.py` | Drift in P2 analytics + incremental reasoning. |
| `epistemic-operations-protocol` | `scripts/check_epistemic_operations_protocol.py` | Divergence between the generated Epistemic Operations manifest digest/field order and the Rust serde DTOs. |
| `exact-release-campaigns-architecture` | `scripts/check_exact_release_campaigns.py` | G-04/G-14/G-15/G-17 campaign regressions. |

### Non-Rust architecture (scope matters — do not confuse these)

| Hook id | Scope | Enforces |
|---|---|---|
| `import-linter-architecture` | Python client `epistemic_graph/`, config `.importlinter` | `epistemic_graph.quant` and `epistemic_graph.embedded` must not import `.client`, `.pool`, or `.parser` — transitively. |
| `dependency-cruiser-architecture` | **`clients/js/` ONLY** — `depcruise --config clients/js/.dependency-cruiser.cjs clients/js/index.mjs` | JS client module rules. It is NOT the Rust crate-graph gate. |

### Hygiene / anti-sprawl

| Hook id | Script | Forbids |
|---|---|---|
| `check-root-hygiene` | `scripts/check_root_hygiene.py` | Any tracked root entry not declared. **Allowlist, not denylist**, and explicitly **not a ratchet**: non-dot root entries need a one-line reason in `.repo-layout.toml`; conventional dotfiles go in the script's `ALLOWED_DOTFILES`. A declared entry that stops being tracked is ALSO a failure. |
| `check-sprawl` | `agent-utilities/scripts/check_sprawl.py` (fleet-shared) | `*_v2.py` / `*_old.py` / `*_new.py` clone filenames, `.orig`/`.rej`/`.bak`, the literal `# --- Merged from` marker, tracked binaries over 1 MB. |
| `check-stubs` | `agent-utilities/scripts/check_stubs.py` | Active stubs and TODOs. |
| `lane-guard` | `agent-utilities/scripts/check_lane_guard.py` | Editing the canonical checkout; stray `CARGO_TARGET_DIR`. |
| `jscpd-differential` / `dupehound-changed-functions` | `scripts/check_duplication.py enforce`, `scripts/check_dupehound.py` | New structural clones / clone pairs in changed code. |
| `complexity-staged` | `scripts/check_complexity_staged.py` | Any NEW function over cyclomatic 10 / cognitive 15, and any regression. |
| `documentation-contract` | `scripts/check_documentation_contract.py` | Cargo/ledger/MkDocs documentation drift. |
| `scale-documentation` | `scripts/check_scale_documentation.py` | Unanchored scaling claims. |
| `constrained-parallelism` | `scripts/constrained_parallelism_gate.sh` | Tests that only pass on a many-core host. Runs `--lib` plus concurrency-sensitive integration binaries under `taskset -c 0,1`. |

**Gate-suite state.** An older `EG-HOOK-FAILURE-CENSUS` aggregate ("40 passed / 6
failed", base `f90753d4`) is **stale** — it does not hold on the current tree, and an
aggregate count never tells you *what* broke. Re-measure per hook. The read-only
Python gates below were re-run by this skill on `1d83cf4b`:

| Hook | Measured |
|---|---|
| `lazy-lifecycle-architecture`, `canonical-property-schema`, `universal-read-rls-architecture`, `mint-lease-call-sites`, `guardrail-tracked-privacy`, `p2-analytics-reasoning-architecture`, `epistemic-operations-protocol`, `exact-release-campaigns-architecture`, `check-root-hygiene`, `documentation-contract`, `scale-documentation`, `check-crates-io-only` | **PASS** |
| `persisted-mutation-contract` | **FAIL** — `mutation-batch module manifest drift: expected ('src/server/mutation_batch/canonical.rs', '…/commit.rs', '…/compile.rs', '…/digest.rs', '…/tests.rs'), observed ()`. The gate expects `src/server/mutation_batch/` to be a module **directory**; the tree has a single `src/server/mutation_batch.rs`. (Its older failure — `missing Rust const inventory: ALL_METHODS` — *is* resolved: the script now imports `method_policy_inventory` and `ALL_METHODS` exists nowhere in `src/` or `crates/`. The gate is red for a **different** reason. Do not mark it fixed.) |
| `current-only-architecture` | **FAIL** — `missing contract block: Method::CreateNodeIfAbsent { .. } => MethodPolicy {`, asserted by `scripts/check_current_only_architecture.py` and absent from the tree. |
| `exact-fault-restart-harness-architecture` | **FAIL** — 18 missing literals across the fault seam (`MutationCommitPhase`, `CertificationFaultSpec`, `EPISTEMIC_GRAPH_CERTIFICATION_FAULT`, `pub fn commit(wtx: WriteTransaction, batch: &MutationBatch)`, …). |
| `p2-modality-architecture` | **FAIL** — `KnowledgeStream retains a claims-only or conditionally fenced served path`. Real defect; owner is the KnowledgeStream/lease owner. Do not relax the gate. |
| `rust-arch-lint` | **FAIL** — see below. |
| `dependency-cruiser-architecture` | **PASSES.** Measured 2026-09-04: `pre-commit run dependency-cruiser-architecture --all-files` -> Passed, with `clients/js/node_modules` ABSENT. This row previously recorded the gate as unable to pass in any clean checkout because `node_modules` is uncommitted and the hook runs no `npm ci`. That reasoning was plausible and wrong -- the gate resolves `4 modules, 3 dependencies` without installed deps. **Re-run a gate before repeating what a document says about it, including this one.** This row was stale within hours of being written. |

Heavy hooks (`cargo-clippy`, `cargo-clippy-all-features`, `cargo-deny-advisories`,
`wheel-smoke`, `pytest`, `constrained-parallelism`) were **not** run here and remain
unmeasured.

**`rust-arch-lint` is RED, and its denominator is measured, not unknown.** One command
(`arch-lint check`, ~2 min, read-only) gives:

```
Found 687 error(s), 3955 warning(s), 0 info(s) in 1077 file(s)
```

**4,642 findings, 687 of them blocking** (`fail_on = "error"`). By rule: AL013
`no-silent-result-drop` 3,845 warn · **AL002 `no-sync-io` 687 error** · AL003
`no-error-swallowing` 58 warn · AL005 `require-thiserror` 52 warn. The recorded "318"
was an **AL001-only** census taken under a stricter config than the hook runs — and
AL001 is the one rule that is disabled. These are historical measurements;
rerun the current command before reporting a count.

> ⚠ **About a quarter of those findings are generated build artifacts.** 858 came from
> `target-isolated/` and 286 from a sibling worktree's `target-*` dir — **1,144 total**,
> leaving a source-tree count nearer **3,498**. `arch-lint.toml` excludes `**/target/**`,
> but `.cargo/config.toml` sets `target-dir = "target-isolated"` and per-worktree dirs are
> named `target-*`, so under 0.5.0 neither that exclude nor `respect_gitignore = true`
> keeps them out (they are `.gitignore`d and scanned anyway). Anyone burning this list
> down will otherwise spend the effort on vendored cranelift/codegen output. **Fix the
> exclude before scoping the work**, and re-measure — your own count will differ with how
> many target dirs are present.

> **Rule that produced several of these:** composing candidates into a repository
> whose gate suite is already red hides the regressions the composition itself
> causes. Keep a named **per-hook** baseline and re-run it after each composition;
> an aggregate pass/fail count cannot tell you what you just broke.

**Path distribution of those 687 blockers** — which directories actually own
the work — is in
[`architecture-reference.md`](architecture-reference.md) → *"Why the placement
matters for effort, not just tidiness"*.

## Evidence behind the gate-authoring rules

The rules themselves are in the parent [`SKILL.md`](../SKILL.md) §4. This is the
evidence each one rests on, so a rule can be checked rather than believed.

### §4.1 — the empty-universe survey

```bash
cd agent-packages/epistemic-graph
for f in scripts/check_*.py; do
  echo "$(grep -cE 'found ZERO|if not (sites|matches|files|hits|found|candidates|rows)\b|len\(.*\) == 0' "$f") $f"
done | sort -n
```

Measured 2026-09-04: **24 of the 27 `scripts/check_*.py` gates return 0** —
no emptiness test of any kind. `check_complexity_staged.py` and
`check_scale_documentation.py` return 1; only
`scripts/check_mint_lease_call_sites.py` returns 2 and turns the test into a
refusal (`:88-95`):

```python
sites = find_call_sites(root)
if not sites:
    raise SystemExit(
        "mint-lease call-site gate failed: found ZERO calls to "
        "mint_graph_policy_lease — either the scan paths drifted or the "
        "feature was deleted; update this gate deliberately if so, don't "
        "let it go quietly blind")
```

⚠ This grep is a **heuristic**, not a proof of vacuity for any single gate: a
gate can be non-vacuous for other reasons, and a hit can be an unrelated
`== 0`. Treat the 24 as the list to audit, and audit the one you are about to
copy from.

### §4.2 — the two universe defects, in full

**A universe that silently grew.** `arch-lint.toml` excludes `**/target/**`, but
`.cargo/config.toml` sets `target-dir = "target-isolated"` and per-worktree dirs
are named `target-*`, so under 0.5.0 neither that exclude nor
`respect_gitignore = true` keeps them out. 858 findings come from
`target-isolated/` and 286 from a sibling worktree's `target-*` — **1,144 of
4,642**, all of them warnings, all of them vendored cranelift/codegen output.
The count was right; the universe was undeclared, so a quarter of the burn-down
would have been spent on generated code (**G10**).

**A universe that silently emptied.** `scripts/_git_subprocess_env.py` exists
because a real `git commit`/`git push` exports `GIT_DIR`, `GIT_INDEX_FILE` and
`GIT_WORK_TREE` into every hook it runs, and `git -C <root> ls-files` does
**not** override them — `-C` only changes the working directory; the repository
those env vars name still wins over path-based discovery. The call then resolves
against the wrong repository, returns an empty or wrong tracked-file list, and
the gate falls back to a raw `rglob` that sweeps in `.venv` and build output.
Confirmed live (BUG-180): a liveness gate reported `orphan_modules: 4 → 196`,
`dead_definitions: 527 → 579` with **zero source changes**, and reproduced
deterministically outside git by setting those two variables by hand.

⚠ **Two independent fixes for that one question now exist**, which is itself the
sprawl this skill is about:

| Primitive | Imported by |
|---|---|
| `scripts/_git_subprocess_env.py` | `check_gitignore_convergence.py`, `check_root_hygiene.py`, `check_tracked_privacy.py` |
| `scanner_contract.run_git` / `scanner_contract.sanitized_env` (`scripts/scanner_contract.py`) | `check_dupehound.py`, `check_duplication.py`, `check_complexity_staged.py`, `list_scanner_sources.py` |
| **neither — bare `subprocess.run(["git", …], cwd=ROOT)` with no `env=`** | `scripts/check_rustfmt_scope.py:44-51`, `scripts/security_sanitizer.py:189-196` |

Adopt one of the two; write neither a third nor a bare call. ⚠ And note that
`_git_subprocess_env.py`'s own docstring names `check_wiring.py` and
`check_current_only_contract.py` as the sites it guards — **neither file exists
in this repo today.** The docstring is stale; **G6** applies to a gate's own
prose as much as to a report's.

### §4.3 — a text-keyed gate calling a move a loss

`scripts/check_exact_fault_restart_harness.py` asserts literal substrings
against one hard-coded file path per contract — `_require(_read("<path>"), {…})`
(`:198-213`, `:216-243`). Running it today
(`python3 scripts/check_exact_fault_restart_harness.py`) reports **18 missing
literals**. Every one is present in the tree, one directory below the file the
gate reads:

| The gate reads | The gate demands | Where it actually lives |
|---|---|---|
| `crates/eg-types/src/mutation_batch.rs` | `pub enum MutationCommitPhase`, `BeforeRows`, `AfterRowsBeforeMetadata`, `BeforeCommit`, `AfterCommitBeforeAck` | `crates/eg-types/src/mutation_batch/model/request.rs:185` |
| same | `struct CertificationFaultSpec`, `const ENV: &str = "EPISTEMIC_GRAPH_CERTIFICATION_FAULT"`, `std::process::abort()`, `spec.request_id != batch.context.request_id`, `operation.domain == spec.domain`, `std::env::var_os(ENV)`, `#[serde(deny_unknown_fields)]` | `crates/eg-types/src/mutation_batch/fault.rs:7`, `:22`, `:57`, … |
| `crates/eg-mutation-store/src/lib.rs` | the four `MutationCommitPhase::*` arms | `crates/eg-mutation-store/src/store/apply.rs:39,103,203,207` |
| same | `pub fn commit(wtx: WriteTransaction, batch: &MutationBatch)` | `crates/eg-mutation-store/src/store/apply.rs:201`, as **`pub fn commit(write: MutationWrite, batch: &MutationBatch)`** |

A file became a module directory; a function moved into a submodule; a parameter
was renamed and its type **tightened** from a raw `WriteTransaction` to the
validated `MutationWrite` — which is precisely the improvement the
`.database()` note in
[`mutation-batch-reference.md`](mutation-batch-reference.md) asks for. The gate
calls all of that a regression.

Its sibling `persisted-mutation-contract` fails the mirror-image way —
`mutation-batch module manifest drift: expected ('src/server/mutation_batch/canonical.rs', …), observed ()`,
i.e. it expects a module **directory** where the tree has a single
`src/server/mutation_batch.rs`. `current-only-architecture` demands the literal
block `Method::CreateNodeIfAbsent { .. } => MethodPolicy {`. Three gates, one
defect class: **path + literal text as the key.**

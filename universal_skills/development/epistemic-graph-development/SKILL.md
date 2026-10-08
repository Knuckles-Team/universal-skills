---
name: epistemic-graph-development
domain: development
skill_type: skill
description: >-
  Develop inside the epistemic-graph (EG) Rust engine without creating sprawl.
  Load BEFORE adding a crate, constant, predicate, table list, helper, gate, or
  second route to an existing capability in agent-packages/epistemic-graph.
  Supplies twelve guardrails with what enforces each; the authorization model
  end to end (claims to VerifiedRequestContext to allows_method to the dispatch
  chokepoint, the RBAC/RLS axis, and the measured kg:read
  / RunUdf / policy:export findings); the 48-crate layer model, the
  dependency-direction rule and how to find a symbol's CONSUMERS; the
  pre-commit gates and what each forbids; the rules for authoring a gate that
  cannot report coverage it does not have; the MutationBatch v1
  scope-vs-domain contract; an anti-sprawl checklist; seven failure patterns;
  and the build/test operating rules. References/ holds the deep material. Use
  when the agent must write, refactor, review, or plan work in the EG Rust
  workspace. Not for the Python agent-utilities side or deploying the engine.
license: MIT
tags: [epistemic-graph, rust, architecture, authorization, anti-sprawl, mutation-batch, gates, cargo]
metadata:
  version: '1.3.2'
  author: Genius
---
# Epistemic Graph (EG) Development

`agent-packages/epistemic-graph` is a Cargo workspace: **48 member crates under
`crates/` plus the root facade package `epistemic-graph` (`src/`)**, root version
`2.27.0`. Its failure mode is not bugs — it is **sprawl**: a second predicate that
answers a question already answered, a hand-copied list of another crate's tables,
a shared helper extracted across a boundary it should not cross.

**Read this file before writing EG code.** Every claim below was verified against
the tree; anything unverified is marked. Verify again — the tree moves.

---

## 0. Mandatory guardrails — read these before §1

Twelve rules. **Every one was broken in this program, usually by someone who had
just written it down** — so each names the failure that produced it and, more
importantly, *what actually enforces it here today*. A rule you have to remember
at the moment of writing is not a guardrail; a rule with a gate behind it is.
Where nothing enforces one, that is stated plainly rather than implied away.
Numbers are cross-referenced to the section that owns them, never restated.

| # | The rule, instantiated for EG | Enforced today by |
|---|---|---|
| **G1** | **State the universe with every number. MUST.** An `arch-lint` count means nothing without which target dirs were in scope; a test count means nothing without the feature set (G3). | **Nothing — discipline.** Self-check: every number you report is followed by the exact command that produced it. |
| **G2** | **A gate's declaration is not its behaviour. Run it. MUST.** `arch-lint.toml` declares `preset = "minimal"` — which `arch-lint list-rules` shows is *AL001 only* — and then disables AL001, so a config-faithful run would enforce **nothing**. 0.5.0 ignores the preset and runs 7 rules. §3 has the measured verdict. | **Nothing — discipline.** Self-check: `arch-lint list-rules`, then cite the gate's OUTPUT with its invocation quoted. Never cite `arch-lint.toml`. |
| **G3** | **"Green" is meaningless without its feature set. MUST.** 133 features; 97 in the `default` closure; **36 outside it.** Procedure + command below. | **Nothing — no hook checks feature closure.** Self-check command below. |
| **G4** | **A fix that passes only its author's own new test has demonstrated nothing. MUST.** §7.1 and §7.5 are both this. Procedure below. | Partly: the `pytest` hook (pre-push/manual) gates the Python integration suite differentially via `scripts/check_integration_baseline.py`. **Nothing scopes the Rust suite for you** — do it by hand, below. |
| **G5** | **Re-derive the consequential closure on every composition. MUST.** A frozen path set describes the base it was cut against, not the base it lands on: MutationBatch v1 was accepted at **18 paths** and composed to **53** (commit `1d83cf4b`). A candidate's recorded path count is a LOWER BOUND, never a scope. | Partly: `persisted-mutation-contract` sources its inventory from `scripts/method_policy_inventory.py` instead of a frozen list, so the method surface re-enumerates itself rather than being frozen (⚠ that hook is RED today for an unrelated reason — §3). Everything else: **discipline.** |
| **G6** | **Verify a claim before acting on it — including from a skill, a brief, or a report. MUST.** The migration contract said `identity.graph_name()`, which does not exist (§5). §7.7 lists four recorded items that were stale *as written*. | **Nothing — discipline.** Cite `file:line` you personally opened. |
| **G7** | **Never delete on island evidence alone. MUST NOT.** A *module* island is a compile fact; a *symbol* island is a lead. Static analysis here cannot see trait objects, macro-generated calls, `#[cfg]` paths, FFI, or string-keyed registries — **and 36 features are outside the default build, so a symbol can look unused purely because you never compiled its feature** (G3 again). | **Nothing — `dead_code` is per-feature-set only.** Trace it by hand before deleting. |
| **G8** | **No baseline files. Ever. MUST NOT.** Verified 2026-09-03: **no `--update-baseline` mechanism exists anywhere in `scripts/`** — the sole mention is `check_tracked_privacy.py:1045` recording that its own was DELETED. Two committed known-bad lists do exist and are the *permitted* shape, not ratchets: `tests/integration_failure_baseline.txt` (79 lines) and `tests/protocol_unbound_baseline.txt` (173 lines). | `scripts/check_integration_baseline.py` — it refuses a malformed line, requires `# owner=@handle review-by=YYYY-MM-DD` per entry, fails when anything NEW joins **and** when anything on the list starts passing. A ledger that rots loudly. **Add no third list, and never add a self-updating flag.** |
| **G9** | **A gate whose universe is empty must FAIL, not pass. MUST.** Vacuous truth is not coverage. | **Enforced by example — copy this shape.** `scripts/check_mint_lease_call_sites.py` exits non-zero on ZERO matches: *"either the scan paths drifted or the feature was deleted … don't let it go quietly blind."* Verified passing today: 1 production call site (`src/server/dispatch.rs:4974`), 1 test-only. Any new gate you write must refuse an empty universe the same way. |
| **G10** | **A count's composition matters as much as its size. MUST.** "Fix the exclude, remove 1,144 arch-lint findings" was true and useless — **0 of those 1,144 were blocking errors.** `arch-lint.toml`'s `exclude` lists `**/target/**` and *not* `target-isolated/**`; verified. §3 owns the breakdown. | **Nothing — discipline.** Break every delta down by rule and severity before calling it progress. |
| **G11** | **Isolation and staging. MUST NOT.** Never edit the canonical checkout; never use the harness's worktree-isolation tool (it sets `core.bare=true` on the shared common dir); never `git stash` (`refs/stash` is repo-wide across 50+ worktrees); never `git add -A`/`.`; never export `CARGO_TARGET_DIR`; never `update-ref` to advance a branch — `merge --ff-only`, then verify by TREE (`git cat-file -e HEAD:<path>`), not by ref. ⚠ **`pre-commit run --all-files` belongs on this list too and §8 currently tells you to run it:** it `git stash`es every UNSTAGED change around the run, and a file-rewriting hook touching the same path can silently DROP those edits on restore. **EG ships no safe wrapper.** Use §8's own replacement — a throwaway detached worktree with a lane-private `PRE_COMMIT_HOME` and `TMPDIR`. (agent-utilities' `scripts/safe_precommit_all_files.py` derives its repo root from `git rev-parse` in the cwd and so is repo-agnostic *in principle*; that is **unverified against EG** — do not treat it as a shipped affordance here.) **§8 "Git, in a shared multi-worktree repo" owns the rest of the list with each prohibition's replacement — read it, this row is only the index.** | `lane-guard` refuses a commit authored in the canonical checkout and a commit made with `CARGO_TARGET_DIR` exported off-lane. **`git stash`, `git add -A`, the harness worktree tool and `update-ref` are NOT enforced — discipline.** |
| **G12** | **Fail closed, and never substitute a sentinel for absence. MUST.** A native scope has no graph name: comparing `Option` against `Some(x)` is correct; an empty-string sentinel is a security defect. Worked instances below. | Partly: `universal-read-rls-architecture` and `mint-lease-call-sites` cover parts of the served-read seam. The scope→`authz_action` mapping is **not gated** — see the two live shapes below. |

### G3 in practice — the feature matrix, and why `--lib` green is not green

Run this. It needs no build and it is the command that revealed the problem:

```bash
python3 - <<'PY'
import re, tomllib
f = tomllib.load(open('Cargo.toml','rb'))['features']
closure, stack = set(), list(f['default'])
while stack:
    x = stack.pop()
    if x.startswith('dep:') or '/' in x or x in closure: continue
    closure.add(x); stack.extend(f.get(x, []))
src = open('src/lib.rs').read().splitlines()
outside = [(m.group(1), g) for i, line in enumerate(src)
           if (m := re.match(r'\s*(?:pub )?mod (\w+);', line))
           and (g := re.findall(r'feature = "([\w-]+)"', src[i-1] if i else ''))
           and not any(x in closure for x in g)]
print("features:", len(f)-1, "| in default closure:", len(closure),
      "| outside:", len(f)-1-len(closure))
print("src/ modules the DEFAULT build does not compile:", outside)
PY
```

Output on `1d83cf4b`: **`features: 133 | in default closure: 97 | outside: 36`**, and
**`src/ modules the DEFAULT build does not compile: [('raft', ['raft'])]`** —
`src/lib.rs:154` gates `pub mod raft;` on the `raft` feature, and `raft` is
reachable only through `cluster`, which is outside `default`.

**Why this is not academic.** `src/raft/` is **32 `.rs` files** (`find src/raft -name '*.rs' | wc -l`). Commit `1d83cf4b` edited
`src/raft/store.rs` — replacing two graph-name comparisons with the fail-closed
`match … scope().graph_name() { Some(g) => …, None => false }` shape, i.e. code
written *specifically to satisfy G12* — and its own verification line reads
*"cargo test -p epistemic-graph --lib at --test-threads=4 reports 1270 passed, 0
failed, 3 ignored."* `--lib` at default features never compiled a line of it.
Separately, `src/raft/cross_shard_txn.rs:845` calls the 3-argument
`eg_mutation_store::read_record` (`crates/eg-mutation-store/src/store/persist.rs:348`);
that call site is *also* compiled by no default build, so nothing in the repo's
routine gate suite has ever type-checked it.

**So: name the build in every acceptance claim.** `1,270 passed` is a statement
about `-p epistemic-graph --lib` under `default`, and about nothing else. If your
diff touches a path behind a non-default feature, you owe a second run:

```bash
cargo check -p epistemic-graph --features raft          # or the feature that gates your path
cargo test  -p epistemic-graph --lib --features <set> -j 8 -- --test-threads=4
```

### G4 in practice — the scoped PRE-EXISTING run, before the full one

Twice in one session a plausible fix compiled and passed the fixture written for
it, and was wrong: the three-class predicate split (caught only by a
**pre-existing** test, §7.1) and the `SqlCatalog`/`Broker` reclassification
(**15 → 27** failures, §5). A scoped run that only covers *new* tests is not
evidence. Do this, in order, before the full run:

1. **Name the touched crates** — the package name equals the directory name for
   all 48 crates (verified), so this mapping is exact:
   ```bash
   git diff --name-only main...HEAD -- '*.rs' \
     | sed -E 's#^crates/([^/]+)/.*#\1#; s#^(src|benches|tests)/.*#epistemic-graph#' \
     | sort -u
   ```
2. **Name the pre-existing test modules that already exercise what you changed** —
   by *symbol*, not by file, because the tests that catch this class live in
   another crate or in an inline `#[cfg(test)] mod` (the 15 → 27 regression was
   caught by `wired_catalog_tests`, an inline module at
   `src/server/wire/mod.rs:5470`, and by `sqlite_wire` — neither is in the
   changed files):
   ```bash
   git grep -n 'mod .*_tests\b' -- src/ crates/ | grep -i '<the thing you changed>'
   git grep -l '<the symbol you changed>' -- src/ crates/ tests/
   ```
3. **Subtract your own new tests** so what remains is genuinely pre-existing:
   ```bash
   git diff --name-only --diff-filter=A main...HEAD
   ```
4. **Run the remainder BY NAME first**, then the crate, then everything:
   ```bash
   cargo test -p epistemic-graph --lib wired_catalog_tests -j 8 -- --test-threads=4
   cargo test -p <touched crate>  --lib -j 8 -- --test-threads=4
   ```
   `--test-threads=4` is not optional — the suite deadlocks at the 24-thread
   default (§8).
5. **Say which pre-existing test would have caught the bug had it been running.**
   If none would have, you have not written the test yet.

### G12 in practice — two live shapes on the current tree

Both verified 2026-09-03; neither is gated, so neither will stop you.

- **An empty rendering set is not "no restrictions."**
  `src/server/policy_export/mod.rs:356` returns `Renderings::default()`, so
  `trino`/`opensearch`/`lakekeeper` come back **empty for a one-marking bundle**,
  pinned empty by its own test at `:718-720`. That is *deliberate* — `DEC-CA-04`
  splits generator from applier and CA-26 owns population — so the renderer is
  not itself the defect. The defect shape is any **applier** that reads an empty
  list as "nothing to enforce". If you write that consumer, fail closed on empty.
- **`policy:export` is cleared by a read scope.** `Method::PolicyExport` carries
  `authz_action = "policy:export"` with `mutates = false`
  (`crates/eg-capabilities/src/domains/security.rs:15`).
  `coarse_kg_admin_only` (`src/server/auth.rs:632`) matches only an `admin:`/
  `security:` prefix or an `:admin`/`:control` suffix, so `policy:export` falls
  past that filter (`src/server/auth.rs:185`) to
  `has("kg:read") || has("kg:write")` (`:193`) — **a plain `kg:read` bearer can
  export the policy bundle.** `src/server/policy_export/mod.rs:100` says the
  non-admin tier was chosen deliberately; whether a *read* scope should clear it
  is a decision someone still has to make, not self-evidently a bug. G6 applies
  to this very bullet: open those four sites before acting on it. **§1 carries
  the full request→decision chain, the chokepoint, and the two other measured
  findings; this bullet is only the G12-shaped instance of one of them.**


---

## 1. The authorization model — who may call what

Four of the five findings a security review produced against this tree are
authorization defects, and not one is a coding error: each reads correctly line
by line and is wrong at the level of the *model*. So this section comes before
the architecture. Read it before you add a `Method`, a `MethodPolicy` row, a
carrier, or a second scope check. Every `file:line` was opened on `2.27.0` for
this section; re-open them (**G6**).

### The request → decision chain

| # | Stage | Where | Establishes |
|---|---|---|---|
| 1 | **Claims arrive as an untrusted wire DTO** | `RequestContextClaims`, `crates/eg-types/src/acl.rs:17` — `principal`, `tenant`, `audience`, `agent_id`, `roles`, `scopes`, `policy_version`, `delegation`, `node`, `priority` | Nothing. Its own doc: *"Callers must not treat a deserialized value as trusted until the server has verified the envelope MAC, deployment audience/tenant/policy version, request binding, and delegation chain."* |
| 2 | **Envelope verification** | `verify_request_with_security_dir` (`src/server/auth.rs:1773`) → `verify_envelope_v2_with` (`:1681`) | `eg2.` prefix → HMAC over the request → clock-skew window → `validate_context_claims` (`:1110`) → `bind_verified_identity` (`:1550`) → non-empty idempotency key → **durable replay-nonce consumption** (`:1709`). Order matters: the nonce is spent last, so a claims-invalid request costs no ledger write. |
| 3 | **Claims → identity binding** | `validate_context_claims` (`:1110`) | Required claims non-empty; no duplicate role/scope/delegation entries; `req.agent_id` matches; **the delegation chain must run principal → agent_id** (empty iff `principal == agent_id`); audience/tenant/policy-version equal the deployment's; a present `node` claim exact-matches this node. |
| 4 | **IdP binding** | `bind_verified_identity` (`:1550` under `oidc`; `:1658` without it) | Every claimed role must appear in the verified token's roles, and **every claimed scope must appear in its scopes or roles** — `"request context asserts unverified scope '{scope}'"`. `require_oidc()` (`:1482`) **defaults to true**, so a build with no configured issuer fails closed rather than accepting HMAC-only identity. **A caller cannot self-assert `kg:read`;** the IdP grants it. |
| 5 | **The trusted wrapper** | `VerifiedRequestContext` (`:60`), built only by `from_verified_claims` (`:68`) | Private fields, so *"downstream code cannot construct a trusted context from caller-supplied JSON."* Two indexes are derived once here (`:69-74`): `scope_index` (scopes verbatim) and `scope_wildcard_domains` (each scope's `":*"` suffix stripped). |
| 6 | **The decision** | **`VerifiedRequestContext::allows_method(action, mutates)`, `src/server/auth.rs:177`** | The one function answering *"may this principal call this method."* Name it exactly; there is no second one. |

`action` and `mutates` are never chosen at the call site — they come from the
capability ledger: `eg_capabilities::policy(&req.method)` yields
`MethodPolicy { authz_action, mutates, durability_domain, audited, emits_cdc, … }`
(`crates/eg-capabilities/src/lib.rs`; rows in `src/domains/*.rs`).
`allows_method` then decides in five ordered steps: (1) `allows_action(action)`
(`:148`) — the **exact** scope, a **domain wildcard** (`graph:*`), or global `*`
→ allow; (2) `kg:admin` → allow, unconditionally; (3)
`coarse_kg_admin_only(action)` (`:632`) — a **string test**,
`starts_with("admin:") || starts_with("security:") || ends_with(":admin") || ends_with(":control")`
→ deny; (4) `mutates` → requires `kg:write`; (5) otherwise →
`kg:read || kg:write`. Step 5 is the fall-through that produces finding 1.

### The scope vocabulary that actually exists

Verified, because the shape is not what its name suggests. **Scopes a caller
holds** are `kg:read` / `kg:write` / `kg:admin` (the coarse aggregates, which
appear only in `allows_method`, `allows_analytics_worker` and the carrier
minters), `*`, `<domain>:*`, and any exact action string. **Actions a method
declares** are the **103 distinct `authz_action` strings** the ledger carries
over its **412 rows** — `node:read`, `compute:finance`, `udf:exec`,
`admin:cluster`, … **none of them `kg:`-prefixed.** The two vocabularies are
disjoint; do not assume an action is spelled `kg:read`. Two dedicated
authorities no coarse grant implies: `analytics:worker` (`:159`) and
`security:bootstrap` (`:163`, which also demands `principal == agent_id`, an
empty delegation chain, and **exactly one** scope). `replicated_mutation`
(`:89`, `raft`) mints `scopes: ["*"]` for the Raft apply task — the one
legitimate `*` holder, reachable only from the state machine after the leader
already dispatched through the full external gate.

### The chokepoint, and what runs beside it

**`check_scope_and_admin_authority` (`src/server/dispatch.rs:5349`) is the
chokepoint.** It has exactly one caller — `dispatch_preamble_checks` (`:5586`) —
and every request reaching `dispatch_inner` (`:5647`) passes through it,
*including* one arriving with an already-verified context, because
`dispatch_with_context(state, req, Some(ctx))` (`:2966`) still runs the preamble.
(`git grep -n check_scope_and_admin_authority` returns the definition and one
call.) In order it applies: **(1)** `check_resource_and_capacity_scope`;
**(2)** `check_cross_tenant_scope` — *"The tenant in a resource body is a
correlation, not an authority claim"*, so only a privileged aggregate reader or
`kg:admin` crosses tenants; **(3)** `allows_method(action, mutates)` (`:5377`);
**(4)** when `is_admin_authz_action(action)` (`src/server/access.rs:1126` —
`action == "security:admin" || action.starts_with("admin:")`), additionally
`require_admin_capability` (`access.rs:1137`) → `IsolationLayer::has_admin_capability`
(`crates/eg-core/src/isolation.rs:1894`): an agent **registered in `rbac.redb`**
with `AgentRole::System` or an explicit RBAC `Admin` grant. No provisioned policy
at all is a **deny**, not a default-open (`access.rs:1152`).

⚠ **Those are two different definitions of "admin" and they disagree.**
`coarse_kg_admin_only` matches **22** action strings; `is_admin_authz_action`
matches **5**. The **17 in the gap — 50 of the 412 methods** — need the
`kg:admin` *claim* but no durable admin grant. `security:audit` is the clean
example: it starts with `security:` so a `kg:write` bearer is refused, but it is
not *equal to* `security:admin`, so `rbac.redb` is never consulted.
`src/server/policy_export/mod.rs:100-105` is the in-tree record of this
asymmetry, written by the lane that hit it.

**A second axis runs after the method gate: per-graph ACL and row-level
security.** Clearing `allows_method` says the *method* is permitted; it says
nothing about *which rows*. That is `check_graph_access` (`access.rs:852`) →
`IsolationLayer::check_access` (`isolation.rs:1508`, default-deny — an actor
with no provisioned identity returns `false` before any graph-type rule runs),
plus `GraphReadAuthority::from_verified` (`access.rs:188`) and
`IsolationLayer::filter_view` (`isolation.rs:1732`). Never treat a scope check
as an isolation check — §7.3's RLS-view-cache finding is what happens when the
two are conflated.

### Call sites outside the chokepoint

`allows_method` has four production call sites that are **not**
`check_scope_and_admin_authority` (`git grep -n allows_method -- src/ crates/`,
excluding tests and comments). `src/server/wire/mod.rs:1245` (SQL-carrier
handshake) and `src/server/bolt_wire/mod.rs:239` / `:409` are **additional
earlier** gates — those requests still reach `dispatch_inner`, so they are not
bypasses. **`src/server/graphql_sub.rs:204` is a genuine parallel path:** it
verifies, calls `allows_method(policy.authz_action, false)`, then goes straight
to `authorized_snapshot` → `check_graph_access` + `GraphReadAuthority::from_verified`
and serves from the graph notifier. It never reaches `require_admin_capability`
or the cross-tenant check — benign today only because `GraphQl`'s action is not
admin-tier, which is a property of one ledger row, not of this code.

> **Rule:** a fifth `allows_method` call site is a fifth place that must
> independently get the surrounding checks right. Add one only with a written
> reason, and say which of the four preamble stages it is choosing to skip.

### Three measured findings

**1 — a bare read scope reaches 221 of 412 methods.** Re-derived for this skill
by parsing `crates/eg-capabilities/src/domains/*.rs` and reimplementing
`coarse_kg_admin_only`'s four string tests (script in the reference below):
**412 rows · 234 non-mutating · 221 reachable by a caller holding only
`kg:read` · 45 distinct actions.** Recheck these historical counts against the
current tree with `scripts/method_policy_inventory.py` and the independent
method in [`references/authorization-reference.md`](references/authorization-reference.md).
The mechanism is step 5: *any* non-mutating
action whose **name** does not match one of four string shapes is granted to any
read-tier caller. **110 of the 221 are `compute:*`** — finance, graph-algo,
datascience, semantic, parse, vision. `mutates` is a **durability** property
being used as an **authorization** property; those are different axes, the same
category error as §5's scope/domain conflation. The narrow fix (one more string
in `coarse_kg_admin_only`) leaves 220 methods unchanged while looking closed;
the general fix is a **declared** coarse posture on the `MethodPolicy` row with
no `Default` impl, so a new method fails to compile until it states its answer.

**2 — `RunUdf` executes caller-supplied code, unaudited, in a default build.**
`crates/eg-capabilities/src/domains/compute.rs:113` declares it
`mutates: false`, `authz_action: "udf:exec"`, `audited: false` — so it clears
`kg:read` and leaves no audit-chain record — and its ledger row carries **no
`#[cfg]`**, unlike `Quantum`, `Asr`, `TtsSynthesize` and `PolicyExport`.
⚠ **Correction to how this is usually stated:** the `Method` variant *is*
feature-gated (`crates/eg-types/src/protocol.rs:2866`, `#[cfg(feature = "wasm-udf")]`;
dispatch arm `src/server/dispatch.rs:11949`) — but `wasm-udf` is inside `full`,
which is inside `default` (verified with the G3 closure script), **so it is
compiled and routed in a default build anyway.** The conclusion holds; the
reason "there is no cfg gate" does not. The sandbox is real (`crates/eg-wasm`:
wasmtime, fuel + memory limits, no host capabilities) — the finding is about who
may invoke it, and that nothing records that they did.

**3 — whether a read scope should clear `policy:export` is an OPEN DESIGN
QUESTION, not a bug.** `Method::PolicyExport` declares `"policy:export"`,
`mutates = false` (`crates/eg-capabilities/src/domains/security.rs:15`), so it
falls through to `kg:read || kg:write`. **`src/server/policy_export/mod.rs:100-105`
records that the non-admin tier was chosen deliberately:** naming it
`"security:admin"` — the obvious first choice, matching
`GetIdentity`/`RegisterIdentity` — would have routed it through
`is_admin_authz_action` and therefore through `rbac.redb` (M7) instead of the
effective request-time role set, *"silently reproducing the exact mistake
DEC-CA-04 A2 corrected."* `src/server/access.rs:2293` carries the same
rationale. So the *admin*-tier decision is settled and documented; what nobody
has decided is whether the **read** tier should clear it. **Do not "fix" this.**
Raise it as a decision, name DEC-CA-04 A2, and let the owner rule. It is also
outside the default build (`policy_export` ∉ the `default` closure), so any
change needs a declared feature set to be tested at all (**G3**).

**Enumerations** — all 103 action prefixes with method counts, the 45 actions a
read scope clears, the two admin definitions and the 17 strings between them,
the six cfg-gated reachable rows with their default-closure status, and the
script that re-derives `412 / 234 / 221 / 45 / 22 / 5 / 50` — are in
[`references/authorization-reference.md`](references/authorization-reference.md).

---

## 2. Where code goes — the layer model

**48 member crates under `crates/` plus the root facade `epistemic-graph`
(`src/`).** Source of truth: `Cargo.toml` `[workspace] members`, the crates'
`Cargo.toml` dependencies, and their public interfaces. The current layer model is:

**0 contract leaves** (`eg-types` — the DAG's bottom and the only crate
everything can see — `eg-durable`, `eg-quantum-core`, `eg-resource`,
`eg-sqlite-format`, `eg-wasm`, `eg-viz-core`) → **1 shared seams**
(`eg-modality`, `eg-mutation-store`, `eg-capabilities`) → **2 modality/index
leaves** (13 crates) → **3 core** (`eg-core`) → **4 storage/transaction**
(`eg-tsdb`, `eg-jobs`, `eg-statechart`, `eg-kvcache`, **plus
`src/server/persistence/`**) → **replication** (**`src/raft/`**) → **5
query/reasoning** (`eg-compute`, `eg-query`, `eg-epistemic`, `eg-plan`,
`eg-rdf`, `eg-shacl`, `eg-shex`, `eg-graphql`) → **6 server/protocol adapter**
(`src/` — there is deliberately **no `eg-server` crate**) → **7 binary
composition** (`[[bin]]` targets behind `required-features`). Plus four
default-off specialty sub-DAGs (quantum ×6, viz ×5, providers ×2, `eg-pyengine`).

Two subtrees the layer table used to omit: **`src/server/persistence/`** (13
files, 21,637 lines) is **Layer-4 storage living inside the Layer-6 facade** —
the `GraphStore` trait plus its one `redb_backend` implementation, not wire
code; **`src/raft/`** (32 files, 29,761 lines, declared at `src/lib.rs:154`) is a
**top-level `src/` module beside the server adapter**, a consensus tier between
storage and dispatch, and it is **outside the `default` build** so no routine
gate type-checks it (**G3**). Together they hold **293 of the 687** arch-lint
blockers (42.6%) — so that burn-down is a storage/consensus workstream.

> **A crate may only `use` crates to its left. No storage or query crate imports
> server dispatch.**

**Enforced by Cargo, not by a lint** — `crates/*` cannot depend on the root
`epistemic-graph` package because the root depends on them, and no
`crates/*/Cargo.toml` declares it. ⚠ That covers `[dependencies]` only;
`[dev-dependencies]` cycles exist and build fine. ⚠ The numbering is a
**target**: three shipped crates already violate it, so use the table to answer
"which direction should this edge point?", never "is this edge legal?"

**The per-crate "what this crate OWNS" tables for all 48 crates, the specialty
stacks, the three violating crates, the dev-dep cycle, the two stale `AGENTS.md`
claims, and the full placement argument with the arch-lint distribution by path
are in
[`references/architecture-reference.md`](references/architecture-reference.md).
Open it before creating a crate or moving a module.**

### Finding a symbol's CONSUMERS before you change it

The direction rule tells you where a *new* thing belongs. It says nothing about
who already holds the thing you are about to change — and with **36 of 133
features outside the `default` closure** (**G3**), the consumer set you can see
is smaller than the one that exists. Four commands; run all four, they answer
different questions:

```bash
# 1. Every crate that DECLARES the dependency — feature-independent, from the manifests.
git grep -n '^<crate> = ' -- 'crates/*/Cargo.toml' Cargo.toml
# 2. The reverse dependency tree cargo will actually BUILD, under one feature set.
cargo tree -i <crate> -e normal --offline                    # default features
cargo tree -i <crate> -e normal --offline --all-features     # the widest set
# 3. Every source reference to the SYMBOL, including tests and benches (a trait impl,
#    a macro body or a string-keyed registry never appears in 1 or 2).
git grep -n '<Symbol>' -- src/ crates/ tests/ benches/ examples/
# 4. Its declaration site, to learn how far it can travel at all.
git grep -n 'pub\( *(crate)\)\? \(fn\|struct\|enum\|const\|trait\) <Symbol>' -- src/ crates/
```

**Why all four.** Measured on `eg-modality`, 2026-09-04: **23 manifests declare
it as a direct dependency**, but `cargo tree -i eg-modality -e normal --offline`
returns **11 nodes** — the rest are optional or behind a non-default feature.
`cargo tree` alone under default features hides more than half the consumers;
the manifests alone tell you nothing about which of them compile the path you
are touching; and neither sees a trait object, a macro-generated call, or a
string-keyed registry — which is exactly why **G7** forbids deleting on island
evidence alone. Visibility is the fourth question: a `pub(crate)` item's blast
radius is one crate and `cargo check -p <crate>` is a complete consumer test; a
`pub` item in `eg-types` can be reached by all 48, and only `--all-features`
sees them all.

---

## 3. What is actually enforced, and what is red today

`.pre-commit-config.yaml` declares **60 hooks**. For the architecture-enforcing
subset — and the contract- and hygiene-enforcing ones beside it — every hook id,
its script, exactly what it refuses, the scope traps in the two non-Rust hooks,
and the per-hook measured PASS/FAIL state with each failure's real message, see
[`references/gates-reference.md`](references/gates-reference.md). **Read the row
there before citing what a gate enforces (G2).** Headlines before you plan work:

- **Nothing checks crate-graph direction.** `arch-lint` 0.5.0 has 8 rules and
  none is a dependency rule; Cargo does that job (§2).
- **`rust-arch-lint` is RED with a measured denominator:** `arch-lint check`
  reports **4,642 findings, 687 blocking** over 1,077 files (re-run 2026-09-04,
  identical to the recorded census). **All 687 are AL002 `no-sync-io`**, and
  **293 (42.6%) sit in `src/raft/` + `src/server/persistence/`**. About a
  quarter of the *warnings* are vendored build artifacts scanned through a
  broken exclude — fix the exclude before scoping the work (**G10**).
- **Four other gates are red** (re-run 2026-09-04): `persisted-mutation-contract`,
  `current-only-architecture` and `exact-fault-restart-harness-architecture` all
  fail on a **path or literal** their contract merely MOVED past — see §4, which
  is about exactly that. `p2-modality-architecture` is the one naming a real
  defect (*"KnowledgeStream retains a claims-only or conditionally fenced served
  path"*); do not relax it.
- **Heavy hooks** (`cargo-clippy`, `cargo-clippy-all-features`,
  `cargo-deny-advisories`, `wheel-smoke`, `pytest`, `constrained-parallelism`)
  are unmeasured here. Do not infer their state.

> **Rule that produced several of these:** composing candidates into a
> repository whose gate suite is already red hides the regressions the
> composition itself causes. Keep a named **per-hook** baseline and re-run it
> after each composition; an aggregate pass/fail count cannot tell you what you
> just broke.

---

## 4. Authoring a gate — how not to ship coverage you do not have

The most repeated failure in this program is not a gate that fails; it is a gate
that **reports coverage it does not have**. One passed on an empty universe; one
measured two of the five properties it claimed; one crashed and still looked
green. A gate is a claim about the world, and an unfalsified claim is worth
nothing. Four rules. The evidence for each — the full worked instances, with the
`file:line` you can open — is in
[`references/gates-reference.md`](references/gates-reference.md) →
*"Evidence behind the gate-authoring rules"*.

### 4.1 Prove it FAILS on a known-bad input before you trust a pass

A gate you have only ever seen pass has demonstrated nothing (**G4**; §7.5 is
the same rule for fixes). Construct the violation the gate exists to catch, run
it, watch it exit non-zero, then remove the violation. If you cannot construct
the bad input, you do not yet know what the gate enforces.

**A gate whose universe is empty must FAIL (G9). Copy this shape** —
`scripts/check_mint_lease_call_sites.py:88-95` refuses its own empty universe
with *"found ZERO calls … either the scan paths drifted or the feature was
deleted … don't let it go quietly blind."* ⚠ It is nearly alone: measured
2026-09-04 across the 27 `scripts/check_*.py` gates, **24 have no emptiness test
at all** and only this one turns a test into a refusal (command in the
reference; it is a heuristic, so audit the gate you copy from).

### 4.2 State the universe and the denominator, in the gate's own output

**G1 applies to gates, not only to reports.** A gate must print what it
*scanned*, not only what it found: "0 violations in 0 files" and "0 violations
in 1,077 files" are different verdicts and most output cannot tell them apart.
Two live instances, both in the reference: a universe that silently **grew**
(`arch-lint.toml` excludes `**/target/**`, but the committed target dir is
`target-isolated`, so 1,144 of 4,642 findings are vendored codegen), and one
that silently **emptied** (a real `git commit` exports `GIT_DIR`/`GIT_INDEX_FILE`
into every hook and `git -C <root> ls-files` does **not** override them; a
liveness gate reported `orphan_modules: 4 → 196` with zero source changes).

Two independent fixes for that second one already exist here —
`scripts/_git_subprocess_env.py` and `scanner_contract.run_git`/`sanitized_env` —
while two gates still call `git ls-files` with no `env=`. Adopt one of the two;
write neither a third nor a bare call. **Test a suspect gate both ways:** plain,
then with `GIT_DIR` and `GIT_INDEX_FILE` set to the worktree's real gitdir and
index. Different answers mean the universe is ambient, not declared.

### 4.3 Never key a gate on a byte offset, a line number, or a symbol name

All three have broken here. A gate keyed on the **text** of the code cannot
distinguish a contract that was **lost** from one that **moved** — and
refactoring moves things, which is the whole point of the work these gates
supervise. The false positive is the expensive direction: it reds the tree,
sends someone to fix correct code, and trains everyone to override the gate.

`scripts/check_exact_fault_restart_harness.py` fails today with **18 missing
literals, every one of which is present in the tree** — a file became a module
directory, a function moved into a submodule, and a parameter type was
*tightened* from a raw `WriteTransaction` to the validated `MutationWrite`. Its
sibling `persisted-mutation-contract` fails the mirror-image way (it expects a
module **directory** where the tree has a file). Full table in the reference.

**Key on behaviour instead**, in this order: **(1)** compile or run it — a
`#[test]` or a trait bound that fails to build is immune to renaming, because
the compiler follows the rename; **(2)** ask the language, not the bytes — parse
(`ast`, `syn`, `tree-sitter`) and assert on the resolved item; **(3)** search the
whole universe, not one path — assert on the *count and location set*, as
`check_mint_lease_call_sites.py` does, so a move re-reports a new location
instead of claiming a deletion; **(4)** if you truly must pin text, pin it
against the HEAD blob's content — never a symbol, a signature, a line number or
a byte offset — say which file it is expected in and *why that file*, and make
the failure message say "moved or missing", not "missing".

### 4.4 A gate is a ledger, not a ratchet

**G8.** No baseline that updates itself; no `--update-baseline` flag (none
exists in this repo — keep it that way). The permitted shape is a reviewed human
ledger, `scripts/check_integration_baseline.py`'s: every entry carries
`# owner=@handle review-by=YYYY-MM-DD`, it fails when something NEW joins **and**
when something on it starts **passing**, and it grows only by a deliberate edit.
Copy that or add nothing. And when you retire a gate, read its tests first — one
of them is probably pinning the bug.

---

## 5. The MutationBatch v1 contract — the two-axis rule

**Authority:** `crates/eg-types/src/mutation_batch/` — `model/request.rs`
(`MutationDomain` + its three predicates), `model/identity.rs` (`MutationScope`,
`MutationScopeIdentity`), `validation.rs`. Ledger: `crates/eg-mutation-store/`.

- **Domain** (`MutationDomain`, 14 variants) names the **operation family**.
- **Scope** (`MutationScope::Graph { graph } | Native { domain, resource }`)
  names the **storage authority** — which store owns the state and its version
  counter.

**They are independent axes, and three different `const fn` predicates answer
three different questions about them** — `may_own_native_scope()` (:101, for
`MutationScope::validate`), `forbidden_in_graph_scope()` (:129, for the
validator), `requires_native_scope()` (:140, the producer's *default*). Reading
a domain's legal scopes off the producer's default is how this went wrong; the
one attempt to collapse them regressed the suite **15 → 27** failures.

> **Scope is a property of the commit ROUTE, which only the caller knows — never
> derive it from the operation-family tag.**

Two rules that bite immediately:

- **Every consumer holds a store + an identity, never a bare `Database`.** ⚠ And
  `MutationStore::write()` is **not** a chokepoint: `pub fn database(&self)`
  hands out the raw redb handle and **17 production sites** call
  `.database().begin_write()`, skipping `validate_physical_root` and
  `validate_handle_write`. §6's *"enforce at the chokepoint"* item failing in
  this very repo.
- **`identity.graph_name()` does not exist.** It is on `MutationScope`; the chain
  is `identity.scope().graph_name()`, returning `Option<&LogicalName>` — and per
  **G12** compare against `Some(x)`, never an empty-string sentinel.

**The full contract — the three domain classes with the validator's exact
accept/reject table, the three predicates with their call sites, the worked
`rbac_persist.rs` reference implementation and its commit sequence, all 17
bypassing `.database()` call sites, and the recorded miswrites — is in
[`references/mutation-batch-reference.md`](references/mutation-batch-reference.md).
Open it before you compile, commit, or validate a batch, or before you give a
store its `MutationScopeIdentity`.**

---

## 6. Anti-sprawl pre-flight checklist

Run **all five** before adding anything. Answer with a command and a file:line,
never from memory — a count without a command behind it is inadmissible.

- [ ] **Does an owner already exist?** `git grep -n '<concept>' crates/ src/`.
      Search the *concept*, not your chosen name: `scope identity`, `bootstrap`,
      `digest`, `invalidate`, `backup_into`. Eight near-identical fixed-scope
      identity builders exist today because eight lanes each searched for their
      own name and found nothing.
- [ ] **Is this constant / predicate / table-list defined in a crate the consumer
      cannot see changes to?** If crate A declares the set and crate B scans for
      it, B will silently go stale. Both must import from a crate they *share* —
      in practice `eg-types`. That asymmetry is exactly how the private-payload
      scan came to know about transaction recovery but not SPARQL.
- [ ] **Is this a second route to an existing capability?** A second call site for
      a minted authority, a second commit route for the same batch, a second
      construction path for the same authority object. `mint-lease-call-sites`
      exists because a second call site is a second place that must independently
      get the security construction right.
- [ ] **Does my predicate answer exactly one question?** Name the caller and the
      question. If two callers ask it, name both questions and check they are the
      same question. Assume they are not until proven otherwise.
- [ ] **If I am extracting a shared helper: which paths did NOT have this control
      before?** List them. Extraction adds behavior to every new caller and
      removes it from none — that is the point and the hazard.

**Where a new thing goes, by kind:**

| Adding | Home |
|---|---|
| A shared constant / wire DTO / predicate two crates consult | `eg-types` (the only crate everything can see) |
| A graph-core capability | `eg-core` |
| A compute domain | `eg-compute` |
| A protocol method | `protocol.rs` variant + `handlers/<domain>.rs` fn + a ONE-LINER `dispatch.rs` arm + a client method + a round-trip test |
| A new operation family | a new `handlers/<domain>.rs`, never another arm in an existing file |
| A store-authoritative capability | its own crate with its own `MutationScopeIdentity`; never a bare `Database` |


---

## 7. Documented failure patterns — the seven rules

The evidence, the `file:line` citations re-verified against the current tree,
and the open/closed status of each are in
[`references/failure-patterns-reference.md`](references/failure-patterns-reference.md)
— **open it before you act on any of these, especially 7.3 and 7.7, which name
things that are still open today.** The rules themselves:

| # | Pattern | The rule |
|---|---|---|
| **7.1** | A predicate consulted by both a validator and a producer is answering two questions | Before reusing a predicate, name its caller and the exact question that caller is asking. Two callers means two questions until proven identical. |
| **7.2** | A hand-copied list of another crate's tables/events cannot stay correct | When a scan in crate A must know a set produced in crate B, the set moves to a crate both can import — in practice `eg-types`. |
| **7.3** | Extracting a shared helper silently ADDS a control to paths that never had one — or REMOVES one | An extraction changes the *set of call sites* a control runs on. Enumerate the paths that lacked it, before and after. **A performance optimization that skips a filter is a security change, and no gate in this repo observes it** — the RLS view cache is still open. |
| **7.4** | Binding identity to a physical path breaks legitimate relocation | Identity derived from a physical location cannot distinguish substitution from relocation. Give relocation one explicit adoption entry point at the boundary that knows it is happening, never at each of the N owners. |
| **7.5** | A fix that passes only the test its author wrote has demonstrated almost nothing | Run the pre-existing suite and say which pre-existing test would have caught the bug. If none would have, you have not written the test yet. |
| **7.6** | Orchestration, not code | A named reference implementation is a copy instruction — extract the shared primitive BEFORE fan-out. File-partitioned lanes prevent edit collisions, not pattern collisions. Never park a lane on a background watcher. |
| **7.7** | Known open items to check before you assume something is broken | Five recorded items, four of which are stale *as written*. **G6** — verify before you act, and before you "fix" one. |

---

## 8. Build and test operating rules

### Running the suite

```bash
export CARGO_INCREMENTAL=0
cargo check -p eg-types                          # fastest inner loop
cargo check -p epistemic-graph                   # full closure
cargo test -p epistemic-graph --lib -j 8 -- --test-threads=4
```

- **Do NOT export `CARGO_TARGET_DIR`.** The committed `.cargo/config.toml` already sets
  `[build] target-dir = "target-isolated"`. That path is *relative*, so it resolves
  against each worktree root — every worktree gets its own isolated target dir with no
  env var and no action after checkout. An exported `CARGO_TARGET_DIR` overrides it
  (cargo's own precedence) and **`lane-guard` refuses the commit** unless the export
  points at exactly this lane's partitioned dir
  (`agent-utilities/scripts/check_lane_guard.py`, `_check_cargo_target_override`).
- **NEVER omit `--test-threads=4`. The suite deadlocks at the 24-thread default.**
- **`-j` bounds the COMPILER, not the harness.** `-j 8` limits `rustc` jobs;
  `--test-threads` after `--` limits the test harness. They are different knobs
  and you need both.
- Cargo ignores `CPUQuota`; `-j` is the only lever. 3-4 concurrent cargo lanes on
  this workspace is the practical ceiling.
- Full gate before claiming done: `pre-commit run --all-files`, no `--no-verify`
  — but **not bare in a shared checkout**, because it stashes and can drop your
  unstaged work (**G11**); run it from a throwaway detached worktree with a
  lane-private `PRE_COMMIT_HOME` and `TMPDIR`, as *Git, in a shared
  multi-worktree repo* below already requires.
  Plus `bash scripts/constrained_parallelism_gate.sh` (GOC-70), which re-runs the
  lib suite and the concurrency-sensitive integration binaries under `taskset -c 0,1`.

### Git, in a shared multi-worktree repo

- **NEVER `git stash`.** `refs/stash` lives in `$GIT_COMMON_DIR` and is repo-wide
  across 50+ worktrees; a `pop` in one lane silently takes another lane's WIP. To
  compare against clean main use `git diff main -- <path>`, `git show main:<path>`,
  or `git worktree add --detach <tmp> main`.
- **NEVER `git add -A` or `git add .`.** Stage an explicit reviewed allowlist:
  `git add -- path/to/file ...`. Re-read `git diff --cached` before committing.
  Handoff notes, baselines, logs, caches and scratch files are never product artifacts.
- **NEVER use the harness's worktree-isolation tool** on this repo — it writes
  `core.bare = true` into the shared config and breaks every linked worktree. Use
  a real `git worktree add "$WORKTREE_ROOT/<repo>/<branch>" -b <branch>` (or
  `rm_worktree add`). Each session takes a distinct branch.
- Do not edit the repository-manager-owned canonical checkout; its background sync
  resets the working tree.
- Run gates in a throwaway detached worktree when a formatting hook could rewrite
  a shared checkout, with a lane-private `PRE_COMMIT_HOME` and `TMPDIR`.


**Disk budgeting, the Rust idioms this workspace has already paid for
(bind-before-yield / E0597, crates.io-only, `bump-my-version` and never a
hand-edited version string, loud feature-gating), and the reporting rules that
govern how a number leaves your hands (no ratchets, the permitted reviewed-ledger
shape, report the real number with its command and its composition) are in
[`references/build-and-test-reference.md`](references/build-and-test-reference.md).
Read the disk section before starting a long build and the reporting section
before publishing a count.**

---

## Resources

| Path | What it is |
|---|---|
| `agent-packages/epistemic-graph/AGENTS.md` | Authoritative repo doc. Its "Module Structure" tree is stale (5 crates vs 48); its "Workspace & server dispatch conventions" section is current. |
| `agent-packages/epistemic-graph/Cargo.toml` | The 48-crate member list and the feature graph. `default = ["graph", "algorithms", "metrics", "full"]` — a **superset** of `full`, not equal to it. |
| `agent-packages/epistemic-graph/.pre-commit-config.yaml` | All 60 hooks. |
| `agent-packages/epistemic-graph/.repo-layout.toml` | Root-entry justification manifest read by `check_root_hygiene.py`. |
| `agent-packages/epistemic-graph/arch-lint.toml` | arch-lint policy. Declares `preset = "minimal"` + `fail_on = "error"` and disables AL001, but 0.5.0 ignores the preset and runs the other 7 rules — see §3. Its `exclude` does not cover `target-isolated/`. |
| `agent-packages/epistemic-graph/.importlinter` | Python client contracts. |
| `epistemic-graph/specs/` | Public repository-owned requirements, architecture, and acceptance evidence for current work. |
| `epistemic-graph/scripts/method_policy_inventory.py` | Re-derives the authorization method inventory discussed in §1. |

### The `references/` directory — what is in each file

| File | What is in it, and when to open it |
|---|---|
| [`references/authorization-reference.md`](references/authorization-reference.md) | The raw enumerations behind §1: all 103 `authz_action` prefixes with method counts, the 45 actions a read scope clears, the two admin definitions and the 17 strings between them, the six cfg-gated rows with their default-closure status, and the script that re-derives `412 / 234 / 221 / 45 / 22 / 5 / 50`. Open it when you need the lists rather than the model. |
| [`references/architecture-reference.md`](references/architecture-reference.md) | The per-crate "what this crate OWNS" tables for all 48 crates by layer, the four specialty sub-DAGs, the three crates that violate the layer numbering, the dev-dependency cycle Cargo does not stop, the two stale `AGENTS.md` claims, and the placement of `src/raft/` + `src/server/persistence/` with the arch-lint blocker distribution by path. Open it before creating a crate or moving a module. |
| [`references/gates-reference.md`](references/gates-reference.md) | Every architecture/contract/hygiene hook, its script and exactly what it refuses; the scope traps in the two non-Rust hooks; the per-hook measured PASS/FAIL state with each failure's real message; the arch-lint denominator with build-artifact contamination broken out. Open it before citing what any gate enforces (**G2**). |
| [`references/mutation-batch-reference.md`](references/mutation-batch-reference.md) | The full MutationBatch v1 contract: three domain classes with the validator's accept/reject table, the three predicates and their call sites, the worked `rbac_persist.rs` implementation and commit sequence, all 17 `.database()` bypass sites, the recorded miswrites. Open it before compiling, committing or validating a batch. |
| [`references/failure-patterns-reference.md`](references/failure-patterns-reference.md) | The seven failure patterns in full — the dated finding behind each, the `file:line` evidence re-verified on the current tree, and which are still open. Open it before acting on any rule in §7. |
| [`references/build-and-test-reference.md`](references/build-and-test-reference.md) | The disk budget one EG target actually needs and why worktree *placement* (not `CARGO_TARGET_DIR`) is the lever; the Rust idioms this workspace has already paid for once (bind-before-yield / E0597, crates.io-only, `bump-my-version` and never a hand-edited version string, loud feature-gating); and the reporting rules — no ratchets, the permitted reviewed-ledger shape, report the real number with its command and its composition. Open it before a long build and before publishing a count. |

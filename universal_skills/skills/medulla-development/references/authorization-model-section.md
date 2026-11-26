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
| 1 | **Claims arrive as an untrusted wire DTO** | `RequestContextClaims`, `crates/medulla-types/src/acl.rs:17` — `principal`, `tenant`, `audience`, `agent_id`, `roles`, `scopes`, `policy_version`, `delegation`, `node`, `priority` | Nothing. Its own doc: *"Callers must not treat a deserialized value as trusted until the server has verified the envelope MAC, deployment audience/tenant/policy version, request binding, and delegation chain."* |
| 2 | **Envelope verification** | `verify_request_with_security_dir` (`src/server/auth.rs:1773`) → `verify_envelope_v2_with` (`:1681`) | `eg2.` prefix → HMAC over the request → clock-skew window → `validate_context_claims` (`:1110`) → `bind_verified_identity` (`:1550`) → non-empty idempotency key → **durable replay-nonce consumption** (`:1709`). Order matters: the nonce is spent last, so a claims-invalid request costs no ledger write. |
| 3 | **Claims → identity binding** | `validate_context_claims` (`:1110`) | Required claims non-empty; no duplicate role/scope/delegation entries; `req.agent_id` matches; **the delegation chain must run principal → agent_id** (empty iff `principal == agent_id`); audience/tenant/policy-version equal the deployment's; a present `node` claim exact-matches this node. |
| 4 | **IdP binding** | `bind_verified_identity` (`:1550` under `oidc`; `:1658` without it) | Every claimed role must appear in the verified token's roles, and **every claimed scope must appear in its scopes or roles** — `"request context asserts unverified scope '{scope}'"`. `require_oidc()` (`:1482`) **defaults to true**, so a build with no configured issuer fails closed rather than accepting HMAC-only identity. **A caller cannot self-assert `kg:read`;** the IdP grants it. |
| 5 | **The trusted wrapper** | `VerifiedRequestContext` (`:60`), built only by `from_verified_claims` (`:68`) | Private fields, so *"downstream code cannot construct a trusted context from caller-supplied JSON."* Two indexes are derived once here (`:69-74`): `scope_index` (scopes verbatim) and `scope_wildcard_domains` (each scope's `":*"` suffix stripped). |
| 6 | **The decision** | **`VerifiedRequestContext::allows_method(action, mutates)`, `src/server/auth.rs:177`** | The one function answering *"may this principal call this method."* Name it exactly; there is no second one. |

`action` and `mutates` are never chosen at the call site — they come from the
capability ledger: `eg_capabilities::policy(&req.method)` yields
`MethodPolicy { authz_action, mutates, durability_domain, audited, emits_cdc, … }`
(`crates/medulla-capabilities/src/lib.rs`; rows in `src/domains/*.rs`).
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
(`crates/medulla-core/src/isolation.rs:1894`): an agent **registered in `rbac.redb`**
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
by parsing `crates/medulla-capabilities/src/domains/*.rs` and reimplementing
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
`crates/medulla-capabilities/src/domains/compute.rs:113` declares it
`mutates: false`, `authz_action: "udf:exec"`, `audited: false` — so it clears
`kg:read` and leaves no audit-chain record — and its ledger row carries **no
`#[cfg]`**, unlike `Quantum`, `Asr`, `TtsSynthesize` and `PolicyExport`.
⚠ **Correction to how this is usually stated:** the `Method` variant *is*
feature-gated (`crates/medulla-types/src/protocol.rs:2866`, `#[cfg(feature = "wasm-udf")]`;
dispatch arm `src/server/dispatch.rs:11949`) — but `wasm-udf` is inside `full`,
which is inside `default` (verified with the G3 closure script), **so it is
compiled and routed in a default build anyway.** The conclusion holds; the
reason "there is no cfg gate" does not. The sandbox is real (`crates/medulla-wasm`:
wasmtime, fuel + memory limits, no host capabilities) — the finding is about who
may invoke it, and that nothing records that they did.

**3 — whether a read scope should clear `policy:export` is an OPEN DESIGN
QUESTION, not a bug.** `Method::PolicyExport` declares `"policy:export"`,
`mutates = false` (`crates/medulla-capabilities/src/domains/security.rs:15`), so it
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

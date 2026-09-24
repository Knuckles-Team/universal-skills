---
name: graphos-ecosystem-development
domain: development
skill_type: skill
description: >-
  Shared development rules for the GraphOS ecosystem repositories
  (epistemic-graph, agent-connector-sdk, agent-utilities, graph-os, their
  front-ends and connectors). Load BEFORE changing any of them, and before
  deciding which repository a change belongs in. Supplies the architecture
  boundaries (EG owns all knowledge and semantics; AU is only the agent
  orchestration plane; graph-os owns the served runtime; the SDK owns connectors,
  packs and transport), the lane protocol (own git worktree, explicit staging,
  --no-verify lane commits, checkpoints), dedicated build hosts, a fanned-out
  landing gate, gate caps, contract regeneration, pipelines@main, identities
  and the decisions protocol; a private overlay skill, when installed, supplies
  host and tooling specifics. Use when the agent must plan, build, review or land
  work in these repos. Repo specifics live in epistemic-graph-development,
  agent-utilities-development, graph-os-development and
  agent-connector-sdk-development.
license: MIT
tags: [graphos, epistemic-graph, agent-utilities, graph-os, agent-connector-sdk, lanes, gates, landing, architecture]
metadata:
  version: '1.3.1'
  author: Genius
---
# GraphOS ecosystem development

The shared rules for every repository in the GraphOS platform. Each rule here was paid
for by an incident; the incident record is in
[`references/traps-reference.md`](references/traps-reference.md). Repository specifics
(layout, test commands, generated artifacts) are in the per-repo skills:

| Repository | Skill |
|---|---|
| `epistemic-graph` (Rust engine + Python client) | `epistemic-graph-development` |
| `agent-connector-sdk` | `agent-connector-sdk-development` |
| `agent-utilities` | `agent-utilities-development` |
| `graph-os` | `graph-os-development` |
| worktrees, gates ledger, merge queue | `repository-manager-*` skills |

The live rulings are in the program's `DECISIONS.md`; the executable designs are in its
`architecture/` directory. When this file and a ruling disagree, the ruling wins — then
fix this file.

## 1. Architecture boundaries — which repository owns the change

One dependency direction — the `workspace.yml` maintenance phases, enforced by the
`phase-direction` gate: **pipelines → epistemic-graph → agent-connector-sdk →
agent-utilities → agent-webui → graph-os → core tools, UIs and skill corpora →
the `agents/*` connectors.** A repository may only import toward the left.

| Owner | Owns | Never |
|---|---|---|
| **epistemic-graph (EG)** | ALL knowledge and semantics: durable storage, the ontology lifecycle, SHACL, RDF, OWL, reasoning, query (UQL/Cypher/SPARQL/SQL), retrieval, memory, usage facts, Decide, ingestion authority (`SourceIngest`), `ConnectorPack`, `GraphSchema`, `WriteBack` records, federation sources. Core schema sources are engine-owned `core:<module>@<version>`. No LLM calls. | host agents, call models, import AU |
| **agent-connector-sdk (SDK)** | Connector construction (`create_mcp_server`), manifests, content packs (skills, prompts, ontologies, shapes) and their certification, source lifecycle and the `connector-sync` runner, governed HTTP/TLS/credentials/OIDC, write-back effects. Every connector goes through the SDK — there is no second connector path. | durable graph state, reasoning, agents |
| **agent-utilities (AU)** | Only the agent orchestration plane: agent graph DAGs, planning and delegation, harness adapters, prompts, model profiles, skills — coordinated and persisted through EG. | ontology/SHACL/RDF/OWL authority; `rdflib`, `pyshacl`, `owlrl`, `owlready2` (runtime or tests); shipped `.ttl`/`.owl`; external graph databases (Neo4j, AGE, Ladybug, FalkorDB — these become EG federation sources); memory stores; a connector toolkit |
| **graph-os** | The served runtime: MCP/REST/A2A composition, the multiplexer and MCP fleet, gateway and control plane, WebUI hosting, messaging daemon and channel adapters, deployment operations. | durable semantics, vendor clients |

Rules that follow from the table:

- **Ask "who owns this?" before "where is it now?"** Much code still sits in AU on its way
  out. Put new work at the target owner; never extend the old location.
- **One contract per boundary.** Consumers import EG-generated client types and senders;
  they never copy wire DTOs, digests or method lists.
- **No compatibility aliases, fallback stores, dual reads/writes or deprecated live paths.**
  A move is one atomic cutover with every consumer updated.
- **A component nothing calls closes nothing.** Wire it into the real served path and test
  that path; a test that only imports a class is not wiring evidence.
- **Enforce at the chokepoint**, the function every caller converges on — never at the one
  entrypoint you were looking at.
- **Connectors never import `agent_utilities`.** They import `agent_connector_sdk`.
- **No per-connector agents.** A connector ships no `agent_server.py` or `<name>-agent`
  console script; graph-os composes the agent over the connector's MCP tools.
- **Names carry no version suffix** (`StorageKernel`, not `StorageKernelV1`). Numeric format
  constants (`*_SCHEMA_VERSION`) are not names.

## 2. The lane protocol

A **lane** is one agent working one scoped brief; an **orchestrator** briefs lanes, owns
the heavy gates and lands finished work. Many lanes run at once on the same repositories.

> **Private overlay.** If a private homelab overlay skill is installed (for example
> `repository-manager-homelab-development`), follow it for host names, the build-runner
> and landing-gate commands, lane directory layout and file names, and the release-train
> mechanics. This skill states only the roles and rules.

**Isolation.** Create your own worktree on a new branch:

```bash
git -C <repo> worktree add <worktree-root>/<repo>/<lane> -b <lane-branch> main
```

- Never use harness worktree isolation (`EnterWorktree`, `Agent(isolation: "worktree")`):
  it writes `core.bare=true` into the shared git config and breaks every linked worktree.
- Never `git stash` — `refs/stash` is one ref shared by every worktree.
- Work only in worktrees you created. Never `git checkout -- <path>`, `git restore`,
  `git reset`, `git clean` or `stash` files you did not write. Unexpected modified files
  mean another lane is working there: stop and report.
- Never edit a canonical checkout; a background sync resets it.
- Need a change in another lane's paths? Write a contract request for the orchestrator
  and continue against a stub.

**Staging and commits.**

- Never `git add -A` or `git add .`. Read `git status --short`, stage an explicit
  allowlist (`git add -- <paths>`, `git add -u -- <path>` for deletions), then re-read
  `git diff --cached --name-status` and `git diff --cached`.
- In a coordinated program, lane commits use `git commit --no-verify`: the orchestrator
  owns the heavy gates and runs them once on the merged tree at landing. Outside one, run
  the gates. Never use `--no-verify` to get past a red gate.
- Never commit with a `user.name` containing `claude`. Use a lane-unique path for commit
  message files, never a shared temp path.
- WIP-commit often (`wip:` subjects are squashed at landing). A commit survives a reset; an
  uncommitted edit may not.

**Checkpoints.** After every commit, build submission and build result, overwrite the lane's
checkpoint file with: branch, worktree, HEAD, pending build ids, uncommitted files and why,
work done / in progress / left, and the exact next action. A resumed lane reads it first.

**Conduct.**

- No sub-agents inside a lane. Scope searches to named files or one repository.
- Run everything in the foreground with a timeout. Never arm a background watcher or poll a
  build; submit it, record the id, and end the turn — the orchestrator resumes you.
- Leave nothing running when your turn ends. Put test temp on disk under the lane's own
  directory (`TMPDIR`, `pytest --basetemp`), never a RAM-backed `/tmp`, and delete it.
- Rebase only when the orchestrator says main moved and it is a safe point; take a landed
  fix instead of writing your own.

**Done** means: all work green on a build, a wrap-up (per-item evidence, what is not done,
exact verify commands) and a review-hotspot list (behaviour-sensitive changes with
`file:line`), the checkpoint marked done, and the commit range reported. Lanes never
merge, land, push or prune.

## 3. Builds — dedicated build hosts, not the shared workstation

- **Never run cargo on the shared development workstation.** One cargo build saturates a
  machine and corrupts other lanes' measurements. Every Rust build and test goes to a build
  host through the program's build runner, as ONE batched submission per round:
  `cargo check` (with `--all-features` for feature-gated modules) first, then the crate's
  tests with `-- --test-threads=4`.
- **Compile first, review second.** Review the compiled tree. After the LAST content edit,
  re-run the tests, not only clippy.
- **Python:** only quick single-file checks locally with bounded workers (`-n 4` max);
  heavier suites go to a non-cargo worker host.
- **EG Python tests locally: only `pytest -m no_engine`.** The others build the engine from
  a fixture; they belong on a build host.
- **AU tests only through `python3 scripts/uv_workspace.py run --all-extras -- pytest …`.**
  Print `sys.executable`; bare `uv run pytest` can fall back to the system interpreter.
- Never export `CARGO_TARGET_DIR`; EG's `.cargo/config.toml` isolates each worktree.

## 4. Gates — design to them up front

Satisfy the gates on the whiteboard. Refactoring to a metric after the fact manufactures new
failures (clone pairs from extracted literals, broken `stacklevel`, lost type narrowings).

| Gate | Cap |
|---|---|
| cccc | cyclomatic ≤ 10, cognitive ≤ 15 per function; no regression of an existing score |
| KISS | statements/fn 35 · args 8 · locals 20 · indentation 5 · returns 8 · bool params 1 · lines/file 900 · fns/file 40 · types/file 20 · interfaces/file 3 · module cycles 0 · dependency depth 4 |
| jscpd | 0 NEW pairs, measured on the combined tree against the release base |
| dupehound | no new structural clones among changed functions |
| type checkers | mypy / `cargo check` clean on every touched file |

Gate-native shapes: an if/else-if chain on a value is a **table**; a `bool` parameter is an
**enum**; guard clauses first, one main path below; decide the module split before writing.
An exhaustive Rust `match` is not complexity — never trade exhaustiveness for a metric and
never add `_ =>`.

**Forbidden, always:** `noqa`, `type: ignore`, `#[allow(...)]`, `nosec`, `skip`, `xfail`,
baseline files, `--update-baseline`, self-updating counts, weakened thresholds. Findings are
tech debt to expose, not to freeze. The one permitted list is a reviewed ledger that fails
when an entry starts passing.

Lanes run only fast targeted checks: `ruff check`/`ruff format`/`mypy` on changed files,
the test files they touched, and one batched `cargo check` (+ their own tests). Use
`pre-commit run -c <config> --files <paths>` for targeted hooks — it skips `always_run`
hooks, so it is never evidence of a full pass. Full suites and `--all-files` belong to the
orchestrator.

Trusting a gate: prove it FAILS on a known-bad input; run the HOOK, not the bare tool
(different universe); test a git-walking gate both plainly and with `GIT_DIR`/`GIT_INDEX_FILE`
set; a gate that scanned nothing must fail, not pass.

## 5. Landing

- Lanes finish and stop. The orchestrator integrates finished lanes per repository onto
  one combined tip, runs a cheap tier first (compile, contract regeneration, lint,
  per-lane targeted tests), then ONE full gate per repository. A red lane is ejected, not
  waited on.
- **The EG landing gate replays the release workflow's jobs** on build hosts. By default
  the jobs are **fanned out** in parallel groups across hosts; a single serial run of every
  job is the escape hatch only. Re-gate a delta by selecting just the affected jobs.
- Green means the FULL release workflow replicated locally — every job and step,
  continuing past failures. A local subset is never "green".
- Measure the merged tree (`git merge-tree --write-tree`), not a branch tip. After any merge
  wave run a parser over every source file (rustfmt / `ast` / `tomllib`) before gates.
- Never land with `update-ref`; fast-forward, then verify by tree (`git cat-file -e HEAD:<path>`).
- Push order follows the phases: pipelines → EG → SDK → AU → WebUI → graph-os → tools/UIs →
  connectors. A project is pushed once its full local gate matrix is green and the
  forge-side prerequisites (Pages, secrets) are verified; then watch hosted CI and fix
  any red at once. Tags and package publication wait for the release phase.
- Prune only after proving reachability with `git merge-base --is-ancestor`, never from
  `git branch --merged` alone.

## 6. Contract regeneration (EG method surface changed)

1. Regenerate on a build host:
   `cargo run --locked -q -p eg-capabilities --features contract --bin gen_contract`, archive
   every artifact it wrote, then run the same command with `-- --check`.
2. Confirm its `wrote N contract artifacts under <path>` line names that build's own source
   directory. Any other path voids both the regeneration and its `--check`.
3. Bring the archive back, compare `sha256sum` on both ends, extract into your worktree.
4. Commit it alone as `chore(contract): regenerate`, citing the build id and sha256.
5. Method-count pins will conflict with other lanes; that is expected — the integrator
   re-sums them at landing. A serde tag rename is a wire change: recompute goldens in the
   same commit.

## 7. Shared conventions

- **pipelines is always referenced at `main`:** reusable workflows `@main`, pre-commit
  `rev: main`, `uvx --from git+…/pipelines@main`. Never a SHA or tag. If a supply-chain gate
  objects, fix its allowlist, not the ref. Third-party sources stay SHA-pinned.
- **Commit identities:** the operator's canonical identity as configured in each checkout;
  AI co-authors only as `Claude <noreply@anthropic.com>` (the `Co-Authored-By:` trailer
  names the model) or `Codex <codex@users.noreply.github.com>`. An author-allowlist gate
  enforces this.
- **Public surfaces:** README/AGENTS.md/docs describe the current product only — no
  machine paths, private endpoints, credentials, internal plan ids or history language.
- **Hook configs live under `.config/`**; after moving one, re-run `pre-commit install -c
  <config> -t pre-commit -t pre-push` or pushes run no gates.
- **Generated artifacts are regenerated, never hand-edited** (contract bindings, connector
  manifests, skill catalogs, `AGENTS.md` where a generator exists).

## 8. Decisions protocol

- Operator-class questions — production identity/secrets, spend, public or privacy
  exposure, scope cuts — go to the orchestrator in the lane checkpoint with the
  trade-offs. Keep working on other items meanwhile.
- Everything else: design the answer yourself, record the ruling in the program's
  decisions record (or the wrap-up for the orchestrator to record), and proceed.
- Explain the implications before asking; never stall a lane on a question.

## How to apply

1. Classify the change with §1 and open the owning repository's skill.
2. Create your worktree and checkpoint file (§2) before the first edit.
3. Design against §4's caps; name the chokepoint and the served path you will test.
4. Build and test on build hosts (§3); regenerate contracts per §6 when the method surface moves.
5. Commit with an explicit allowlist (`--no-verify` only as a coordinated lane), checkpoint,
   and write the wrap-up and review hotspots when everything is green.

Execution: agents run this directly — it is a rulebook, not a DAG. When graph-os is
reachable, a delegated agent can load it through `graph_orchestrate` and the same rules
apply unchanged. Use an economy model for inventory, searches and mechanical edits; keep the
strongest model for design, integration and security-sensitive review.

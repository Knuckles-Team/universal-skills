---
name: workspace-validator
domain: development
skill_type: skill
description: >-
  Agent workflow for validating the workspace using repository-manager MCP tools, fixing issues concurrently across all projects until 0 errors remain, and optionally bumping versions and pushing. Also audits worktree and git state — classifying which worktrees are merged (safe to prune), in-flight (do not disturb), or dangling, and which projects have unmerged/unpushed changes. Use when the user asks to validate projects, run repository-manager validation, fix all project errors, ensure all projects are valid, or check which worktrees/projects are dangling, in flight, or safe to prune.
license: MIT
tags: [validation, workspace, repository-manager, bugfix, workflow, worktree, git-state]
metadata:
  version: '1.0.2'
  author: Genius
---
# Workspace Validator

This skill defines the autonomous workflow for systematically validating all projects in the workspace, reviewing and fixing the identified issues concurrently, and optionally publishing updates. Validation runs as a **background job** per repository using `rm_projects`. The tool returns a job dictionary immediately, and you poll for results using `action="validate_status"`.

## ⚠️ Requirements
- Ensure the `repository-manager` MCP server is active so you have access to `rm_projects`, `rm_git`, and `rm_workspace` tools.
- DO NOT use the CLI `repository-manager` command for validation. You must use the MCP tools to optimize token usage.
- **NEVER manually edit pyproject.toml versions, commit, tag, or push releases.** All maintenance must be driven automatically via the `repository-manager` using the `auto_bump` and `auto_push` parameters.
- **Topological Release Order (`CONCEPT:RM-TOPOLOGY`):**
  - **Phase 3:** `agent-utilities` must be bumped and published first.
  - **Phase 4:** Core Tools & UIs (including `geniusbot`, `agent-terminal-ui`, `agent-webui`, `universal-skills`, `skill-graphs`) consume `agent-utilities`. Bumping `agent-utilities` triggers automated dependency updates in Phase 4 projects.
  - Circular dependencies are prevented by the `repository-manager` skipping dependency updates for any project belonging to a phase lower than the currently bumped phase.
- **Change-aware start (`CONCEPT:RM-PHASE-START`):** `auto_bump` and `auto_push` do not blindly start at Phase 1. The backend detects the **lowest phase that actually has repository changes** and begins there, cascading to every later phase and skipping unchanged upstream phases (and their inter-phase `wait_minutes`). Because phases are topologically ordered, a change in phase *N* only ever affects phases `>= N`, so this is safe. Practical effect: editing one Phase-4 repo runs Phase 4 onward without sitting through the Phase-3 wait; if nothing changed anywhere, the bump/push is a no-op. A repo counts as changed when it is not both clean and in sync with origin (uncommitted changes, an unpushed feature commit, or an unpushed bump). You do not configure this — it is automatic whenever `auto_bump`/`auto_push` are set.

## ⚠️ Error Resolution Policy

> **CRITICAL:** When fixing validation errors, you MUST follow these rules:

1. **NEVER prefix variables with an underscore (`_`) to silence linting errors.** This is strictly prohibited. Renaming `var` to `_var` is not a fix — it's hiding the problem.
2. **Always determine root cause.** For every error, understand how the variable, implementation, or code was *intended* to function. Close the knowledge gap before making changes.
3. **Fix the real problem.** If a variable is unused because a feature is incomplete, complete the implementation. If it's genuinely dead code, remove it entirely — don't rename it.
4. **Troubleshoot ALL errors.** Every single error in the report must be understood and resolved at its root cause. No exceptions.

## 🧪 Poison Pill Detection

> **CRITICAL:** Before starting any validation run, be aware of **workspace-level cascading failures**.

The root `pyproject.toml` uses `uv` workspace globs (e.g. `agent-packages/agents/*`) to include all projects. If **any single project** in that glob has a malformed or missing `pyproject.toml`, the entire workspace resolution fails. This causes **every** project's pytest phase to report the same error:

```
error: Workspace member `/path/to/broken-project` is missing a `pyproject.toml`
```

**Detection:** If the `rm_projects` JSON results show the exact same error message across many or all projects pointing at a single workspace member, that project is the "poison pill".

**Resolution:**
1. Navigate to the broken project directory.
2. Verify its `pyproject.toml` exists and is valid PEP 517 compliant:
   - Must have `[build-system]` with `build-backend = "setuptools.build_meta"` (NOT `build_meta`).
   - Must have a `[project]` section with `name` and `version`.
3. Fix or create the `pyproject.toml`, then re-run validation.
4. **Do NOT waste time fixing individual project pytest errors when the root cause is a poison pill.** Fix the pill first; the cascading errors will disappear.

## Workflow Instructions

### Phase 1: Clarification
1. When triggered, first clarify with the user if they only want to validate and fix issues, or if they *also* want to perform a phased bump (e.g. minor version) and phased push once 0 issues are found.
2. If not specified by the user, the default behavior is to ONLY validate and fix. Do not proceed to bumping/pushing unless explicitly confirmed.

### Phase 2: Parallel Validation
3. For the **first run**, submit validation using the `rm_projects` MCP tool with `action="validate"`. Do NOT pass the `repositories` parameter on the first run — validate all projects.
4. The tool runs asynchronously and immediately returns a **terse submission** (`queued_count` + `queued_projects`) — not a giant id map.
5. **Poll for Progress (terse by default):** Call `rm_projects` with `action="validate_status"`. It returns a COMPACT roll-up (`summary=true` is the default) so it stays inline-returnable even at **thousands of repos**:
   - `summary`: `{total, completed, running, failed, passed}` counts.
   - `running_projects`: names still validating.
   - `failed_projects_csv`: comma-separated failures.
   - `failed_details`: `{repo: {job_id, failures:[...]}}` — exact hook failure messages for ONLY the failed repos.
   - (Pass `summary=false` for the full per-job `jobs` dict — avoid at scale; it can exceed the response limit and spill to a file.)
6. **Analyze the Return:** Use `failed_details[repo].failures` for the exact hook output to fix; `failed_projects_csv` is the failure set.
7. **Monitor:** Continue polling `validate_status` (reasonable intervals) until `summary.running == 0`.

### Phase 3: Remediation Loop
You will enter a continuous loop of fixing issues based on the JSON hook outputs.

8. **Manual Fixes:** For any remaining issues (e.g. static analysis, failing tests), follow the **Error Resolution Policy** above strictly. Fix issues concurrently across different projects.
9. **Re-Validate ONLY the failures:** After applying fixes, call `rm_projects(action="validate", failed_only=true)`. This auto-targets exactly the repos whose most-recent validation failed (and forces past the cache) — do NOT re-run the whole workspace during remediation. (You may instead pass `repositories="repo1,repo2"` to target a specific subset.) A repo that now passes drops out of the failed set automatically.
10. Poll `validate_status` (summary). If `summary.failed > 0`, repeat from step 8 on the new `failed_projects_csv`. Continue until `failed == 0`.

### Phase 4: Final Regression Sweep & Release
11. **Ecosystem-wide clean gate:** Once `failed_only` reruns reach 0 failures, run ONE final validation against **ALL** repositories (no `repositories`, no `failed_only`, `force_revalidate=true`) so the entire dependency graph is verified green together — fixing one repo can regress a dependent. If the user confirmed bump+push in Phase 1, cascade this final all-repos run into the release by adding `auto_bump=true` and `auto_push=true`.
    - **Committing feature code (not just version bumps):** when uncommitted/new feature code is in the working tree, add `commit_code=true` + `commit_message="..."`. The backend then runs a concurrent **stage (`git add -A`) → pre-commit → commit** pass across all targeted repos AFTER validation passes and BEFORE the bump, so untracked/new files are committed (the bump and push no longer rely on a tracked-only `git add -u` safety net). The bump waits on this step. This is the tool-driven equivalent of "add all of our code, pre-commit, then bump." Standalone equivalents exist as `rm_git(action="pre_commit")` and `rm_git(action="commit_code", message=...)`.
    - **Worktree hygiene (automatic, report-only):** whenever `auto_bump`/`auto_push` is set, the release chains a final `worktree_hygiene` job after the bump/push and returns its `worktree_hygiene_job_id`. By **default it only reports** — its result carries the same audit classification (`safe_to_prune`, `do_not_disturb`, `summary`) so you can see which session worktrees are already merged into `main` without anything being deleted. Add `prune_worktrees=true` to make that step actually remove the `merged` worktrees (and `dangling` admin pointers) — it **never** touches `active`/in-flight work or orphaned directories. This is the audit-aware cleanup that replaces blind reaping; surface the `safe_to_prune` list to the user before opting in.
12. **CRITICAL:** Before running any validation with `auto_bump=true`, call the `rm_workspace` tool with `action="list_branches"`. Verify that every single project is currently on the `main` branch. If any project is on a different branch, you MUST stop and ask the user how to proceed, or align them back to `main` before validating with the bump flag.
13. The backend will now orchestrate the entire sequence in a single background job. Poll `action="validate_status"` until the job completes. The results will contain the validation summary, and if successful, the `bump` and `push` release results plus the `worktree_hygiene_job_id` (poll it for the worktree audit/prune outcome). The bump and push **auto-start at the lowest phase that changed** (see Change-aware start above), so a release touching only later-phase repos will not replay earlier phases or their waits; if no repo changed, the bump/push reports a no-op.
14. If the full sweep passes and the release occurs, you are done. If new validation regressions are revealed, the bump/push will be safely aborted by the backend, and you must repeat the remediation loop.

## Worktree & Git-State Hygiene Audit

Many concurrent agent sessions work the `agent-packages/*` repos in their own git
worktrees under `/home/apps/worktrees/<repo>/<branch>` (CONCEPT:RM-WORKTREE). Over
time these accumulate: some are already merged into `main` and just clutter, some
hold live in-flight work that must NOT be disturbed, and some go stale or dangling.
Use the audit to see the whole picture before pruning or releasing — it answers
"which projects have unmerged/unpushed changes, and which worktrees are safe to
remove vs actively developed."

### Running the audit (read-only by default)

Call `rm_worktree(action="audit")`. It is **non-destructive** unless you pass
`prune_merged=true`. It returns:

- `summary` — counts per class (`merged`, `active`, `stale`, `dangling`, `orphans`,
  `unpushed_repos`).
- `worktrees` — one entry per linked worktree with `class`, `dirty`, `ahead`,
  `behind`, `merged`, `last_commit_age_days`, and `base_unpushed`.
- `repos` — every canonical repo's git state: `class ∈ {clean, dirty, unpushed}`,
  `ahead_origin`/`behind_origin`, `no_upstream`, `base_unpushed`.
- `safe_to_prune` / `do_not_disturb` / `review` — pre-bucketed worktree lists.
- `orphans` — directories under the worktree root that look like worktrees but no
  repo tracks (reported, **never** auto-removed — they may hold uncommitted work).

### Interpreting the classes

| Class | Meaning | What to do |
|-------|---------|------------|
| `merged` | clean **and** the branch tip is already an ancestor of local `main` — work is captured | **safe to prune** |
| `active` | dirty, or unmerged-and-ahead with recent commits | **DO NOT disturb** — live development |
| `stale` | unmerged + ahead but quiet longer than `stale_days` (default 14) | surface to the user for a decision |
| `dangling` | detached HEAD, deleted branch, or missing-on-disk admin entry | prune candidate |

A worktree counts as `merged` once its branch is in **local** `main`, even if `main`
itself has not been pushed yet — the work is not lost, the worktree is just
redundant. When that worktree's `base_unpushed` is `true`, remind the user that
`main` still owes a push (drive it via the phased push in Phase 4), but the worktree
is still prunable.

### Pruning

After surfacing `safe_to_prune` to the user, prune either way:

- **One-shot:** `rm_worktree(action="audit", prune_merged=true)` — removes every
  `merged` worktree (and deletes its branch) and prunes `dangling` admin pointers in
  a single call. It **never** touches `active`/`stale` work or `orphans`, and never
  force-removes a dirty tree. The result includes `pruned` and `kept` (with reasons).
- **Per item:** `rm_worktree(action="remove", repo=..., branch=..., delete_branch=true)`
  when you want to remove worktrees individually.

Because `prune_merged=true` deletes worktrees and branches, the repository-manager
Universal Tool Guard treats it as a sensitive call — confirm the `safe_to_prune`
list with the user before running the one-shot sweep.

### Tie-in with releases (Phase 4)

The release pipeline runs this audit **for you**: a `validate` with
`auto_bump`/`auto_push` automatically chains a `worktree_hygiene` job after the
bump/push and returns its `worktree_hygiene_job_id` (see Phase 4, step 11). That job
is **report-only by default** — poll it for the `safe_to_prune`/`do_not_disturb`
classification — and only deletes when you pass `prune_worktrees=true`, and even then
only `merged`/`dangling` worktrees, never in-flight or orphaned ones. So the release
both surfaces in-flight worktrees (`do_not_disturb`) and offers safe, opt-in cleanup
in a single flow.

The Phase 4 pre-bump check also calls `rm_workspace(action="list_branches")` to
confirm every project is on `main`; you can still run `rm_worktree(action="audit")`
standalone at any time for an ad-hoc snapshot.

## Scaling to thousands of repositories

The validator is built to scale; keep these in mind for very large workspaces:

- **Always poll with the default terse `summary=true`.** The full per-job dump
  grows linearly with repo count and will exceed the response limit (spilling to
  a file) past a few hundred repos. The terse roll-up (counts + `failed_details`
  + `failed_projects_csv`) stays small regardless of workspace size.
- **Remediation re-runs use `failed_only=true`, never the whole workspace.** This
  keeps each loop O(failures), not O(repos). Only the FINAL gate validates all.
- **Tune concurrency with `RM_MAX_WORKERS`** (env on the repository-manager MCP
  server). Default caps the worker pool at **min(20% CPU, 20% RAM)** of the host
  (env-tunable: `RM_CPU_FRACTION`, `RM_RAM_FRACTION`, `RM_WORKER_MEM_GB`); set
  `RM_MAX_WORKERS` to override outright. Each validation runs pre-commit + pytest,
  so it's CPU/IO-heavy. The same throttle governs the `commit_code` pass.
- **Validation is cached** (`force_revalidate=false` default): unchanged repos
  return cached results instantly, so repeated full sweeps are cheap. Use
  `force_revalidate=true` only for the failed set and the final gate.
- **Topological release stays phase-ordered** (`agent-utilities` → dependents) so
  PyPI dependencies publish before the projects that consume them.

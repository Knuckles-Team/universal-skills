---
name: arbora-development
domain: development
skill_type: skill
description: >-
  Develop in any Arbora ecosystem repository from public GitHub sources.
  Route ownership, bootstrap source checkouts, and verify repository-owned
  specs across the Arbora core, public frontends, pipelines, finance and
  infrastructure agents, and the organization hub.
license: MIT
tags: [arbora, development, public-contribution]
metadata:
  version: '1.5.2'
---

# Arbora ecosystem development

For a contributor or coding agent starting with no ecosystem context, open
the public [organization hub](https://github.com/Knuckles-Team/.github), its
[build-first queue](https://knuckles-team.github.io/.github/build-first.html),
and [contribution guide](https://github.com/Knuckles-Team/.github/blob/main/CONTRIBUTING.md).
The queue links owner-native specs in epistemic-graph, connector SDK,
agent-utilities, arbora, WebUI, repository-manager, pipelines,
agent-terminal-ui, emerald-exchange, tunnel-manager, and the hub itself.

The canonical, complete instructions are packaged by
[`arbora`](https://github.com/Knuckles-Team/arbora/blob/main/arbora/skills/arbora-development/SKILL.md).
Read that `SKILL.md` and its
[`bootstrap.md`](https://github.com/Knuckles-Team/arbora/blob/main/arbora/skills/arbora-development/references/bootstrap.md)
from the current public checkout before changing any ecosystem repository.
The Arbora package registers the skill through its
`agent_connector_sdk.connector` entry point; this catalog entry lets a
contributor discover it before installing Arbora.

Use `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `sdd-implementer`, and
`sdd-full-lifecycle` from this public skill kit for the specification and
implementation sequence. The owner repository's spec remains the authority.

Use only the repository-owned `specs/<id>/` and public code/contracts as the
implementation authority. The spec must be self-contained for contributors
without private drafts, inventory, credentials, or a live deployment.

## Spec-driven flow

Run this before any code. Full table and gates: the Spec-driven development section of `AGENTS.md` and the [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md).

1. Read `.specify/memory/constitution.md`; create it from pipelines `specs/_template/constitution.md` if absent (`speckit-constitution`).
2. Specify the feature: `speckit-specify` gathers the inputs and writes `specs/<stable-id>/spec.md` and `requirements.md`.
3. Clarify: resolve every `[NEEDS CLARIFICATION: ...]` marker (`speckit-clarify`).
4. Plan: `plan.md` from pipelines `specs/_template/plan.md`, including Build contract, Production caller chain and Cross-repo seams (`speckit-plan`).
5. Tasks: `tasks.md` lines `- [ ] T001 [P] [US1] <ROW-ID> ...` (`speckit-tasks`).
6. Analyze: fix the gaps and fill `checklists/requirements.md` (`speckit-analyze`).
7. Implement and land with the delivery contract in this skill (`speckit-implement`); release through pipelines `releases/*.yml` bundles.

Never write code for a row that is not SPECIFIED. Feature directories use the stable spec ID, never a numbered prefix. The state is computed from rows, `Spec:` trailers and test bindings; never write `status.json` or a `Status:` line.

---

## Rapid delivery: the 5-minute contract

Specs are already designed. The work is implementation, delivered in very small, continuously landed slices.

**Time and size**
- One agent delivers one PR in 5 minutes or less. No agent or sub-agent runs longer than 5 minutes; an orchestrator dispatches the next slice to a fresh agent.
- CI turns around in 5 minutes or less. PR CI runs the fast subset: lint, type check, the spec check, and only the tests and crates the diff touches. Pushes to main run the full suite.
- Never spawn sub-agents from a delivery agent.

**Investigation budget**
- At most 2 minutes and about 10 tool calls of reading before the first edit, and at most about 25 tool calls per PR.
- If the change is not clear by then, ship the `.1` slice (typed model plus refusal test) or skip the row with a one-line note. Do not write deferral essays.
- Trust the orchestrator's evidence and ID list; do not re-verify it.

**Sizing (deterministic)**
- Split a requirement when its size score is above 6, it names more than 2 code roots, or it is cross-repo. Children are `<ID>.<n>`, producer first.
- Net-new work is sliced, never skipped: `.1` typed model plus validation and refusal tests, `.2` the one entry point that uses it, `.3`+ each further behavior.
- Cross-repo moves split into one child per repo: the destination copies the behavior first, then the source switches importers and deletes.

**Before every push**
- Work in a real `git worktree add` from `origin/main`. Never edit a shared checkout, never `git stash`, never `git add -A`, never force-push.
- Run the repo's own pre-commit on the changed files: `uvx --from pre-commit==4.6.0 pre-commit run --files $(git diff --name-only origin/main...HEAD)`. Fix every failure. No `noqa`, `type: ignore`, skip, xfail or whitelist entries to pass a gate.
- Run the targeted tests only, never a full suite.

**Landing**
- Every PR lands within minutes of going green; no PR sits idle. Mechanical conflicts (generated files, Markdown) are resolved automatically by the merge-train tool. Real conflicts are additive in most cases and are resolved, not deferred.
- Many open PRs land together as a merge train (one integration branch, one CI run), built with the orchestrator's merge-train tool.
- Full CI on main catches what the fast subset missed; regressions are fixed forward immediately.
- Landing in this repo: `gh pr merge --auto --merge` when the PR opens. The required checks are the fast PR subset. If the PR goes DIRTY, merge `origin/main` into it and push.

**Report**: at most 8 lines: PR URL, requirement IDs, test result, and any `ID:<main sha>` proof for rows already on main.

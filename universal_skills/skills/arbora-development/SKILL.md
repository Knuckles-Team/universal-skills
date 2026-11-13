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
  version: '1.6.0'
---

# Arbora ecosystem development

For a contributor or coding agent starting with no ecosystem context, open
the public [organization hub](https://github.com/Knuckles-Team/.github), its
[build-first queue](https://knuckles-team.github.io/.github/build-first.html),
and [contribution guide](https://github.com/Knuckles-Team/.github/blob/main/CONTRIBUTING.md).
The queue links owner-native specs in medulla, connector SDK,
meristem, arbora, WebUI, repository-manager, pipelines,
agent-terminal-ui, emerald-exchange, tunnel-manager, and the hub itself.

The canonical, complete instructions are packaged by
[`arbora`](https://github.com/Knuckles-Team/arbora/blob/main/arbora/skills/arbora-development/SKILL.md).
Read that `SKILL.md` and its
[`bootstrap.md`](https://github.com/Knuckles-Team/arbora/blob/main/arbora/skills/arbora-development/references/bootstrap.md)
from the current public checkout before changing any ecosystem repository.
The Arbora package registers the skill through its
`scion_sdk.connector` entry point; this catalog entry lets a
contributor discover it before installing Arbora.

Use `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `sdd-implementer`, and
`sdd-full-lifecycle` from this public skill kit for the specification and
implementation sequence. The owner repository's spec remains the authority.

Use only the repository-owned `specs/<id>/` and public code/contracts as the
implementation authority. The spec must be self-contained for contributors
without private drafts, inventory, credentials, or a live deployment.

## Spec-driven flow

Run this before any code. Full table and gates: the Spec-driven development section of `AGENTS.md` and the [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md).

1. Read `.specify/memory/constitution.md`; create it from `.specify/templates/constitution-template.md` if absent (`speckit-constitution`).
2. Specify the feature: `speckit-specify` gathers the inputs and writes `specs/<stable-id>/spec.md` and `requirements.md`.
3. Clarify: resolve every `[NEEDS CLARIFICATION: ...]` marker (`speckit-clarify`).
4. Plan: `plan.md` from `.specify/templates/plan-template.md`, including Build contract, Production caller chain and Cross-repo seams (`speckit-plan`).
5. Tasks: `tasks.md` lines `- [ ] T001 [P] [US1] <ROW-ID> ...` (`speckit-tasks`).
6. Analyze: fix the gaps and fill `checklists/requirements.md` (`speckit-analyze`).
7. Implement and land with the delivery contract in this skill (`speckit-implement`); release through pipelines `releases/*.yml` bundles.

Never write code for a row that is not SPECIFIED. Feature directories use the stable spec ID, never a numbered prefix. The state is computed from rows, `Spec:` trailers and test bindings; never write `status.json` or a `Status:` line.

---

## Delivery contract

Specs are already designed. The work is implementation.

**A row is delivered when**
- its behaviour is fully implemented, as the row says;
- it is wired to its production entry point (a production caller exists outside the new code and its tests);
- every test level its test-spec names passes;
- the tests are bound to the row;
- the gates verify it.

There is no time limit, no size limit per agent or per change, and no rule about how many agents deliver a row.

**Recommendations (optional)**
- Group rows that share an entry point into one bundle and deliver bundles in dependency order, producer first. Split a requirement into `<ID>.<n>` children when it names more than 2 code roots or is cross-repo; the destination repository copies a behaviour first, then the source switches importers and deletes.
- Net-new work can be sliced: `.1` typed model plus validation and refusal tests, `.2` the one entry point that uses it, `.3`+ each further behaviour.
- Trust the orchestrator's evidence and ID list rather than re-verifying it.
- Run the targeted tests for the change; leave the full suite to the main-branch gates.
- Open PRs can land together as a merge train, built with the orchestrator's merge-train tool.
- Report the PR URL, requirement IDs, test result, and any `ID:<main sha>` proof for rows already on main.

**Before every push**
- Work in a real `git worktree add` from `origin/main`. Never edit a shared checkout, never `git stash`, never `git add -A`, never force-push.
- Run the repo's own pre-commit on the changed files: `uvx --from pre-commit==4.6.0 pre-commit run --files $(git diff --name-only origin/main...HEAD)`. Fix every failure. No `noqa`, `type: ignore`, skip, xfail or whitelist entries to pass a gate.

**Landing**
- Mechanical conflicts (generated files, Markdown) are resolved by the merge-train tool. Real conflicts are additive in most cases and are resolved, not deferred.
- Full CI on main catches what the pull-request subset missed; regressions are fixed forward.
- Landing in this repo: `gh pr merge --auto --merge` when the PR opens. The required checks are the fast PR subset. If the PR goes DIRTY, merge `origin/main` into it and push.

## Delivery practice

Follow the [delivery practice reference](https://github.com/Knuckles-Team/pipelines/blob/main/reference/delivery-practice.md) for waiting, branches, merge holds, worktree safety and verification. The [constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) holds the binding articles: XXVIII (merges and releases), XXIX (checks tell the truth), XVIII (landed means reachable), XXV (small units) and XXXII (written text is self-evident: every pull request, review or issue comment and commit message states what changed, why, the behaviour impact and how it was verified, in plain words, with no hostname, private domain, local path, internal tool, private repository, workflow jargon or private handoff pointer, and every spec row ID beside its one-line meaning).

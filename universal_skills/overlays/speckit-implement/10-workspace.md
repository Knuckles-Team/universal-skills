---
mode: append
---
## Delivery contract

- Never write code for a row that is not `SPECIFIED` in this repository's `specs/`. If no row owns the behavior, extend the owning spec first.
- Bind each test to its row: `@pytest.mark.spec("ID")`, `# spec: ID` or `// spec: ID`.
- Commit one logical change at a time with a `Spec: <IDs>` trailer (or `Spec: none (<reason>)`) directly above the `Co-Authored-By:` trailer. Stage explicit paths only.
- Order the work as plan, implementation slices that touch different files in parallel, tests, review, then merge. Run the repository gate (`uvx pre-commit run --all-files`) before you push; never bypass hooks.
- Run the repository's CCCC, `jscpd` and Dupehound gates where configured; a missing tool is a reported gap.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

## Delivery practice

Follow the [delivery practice reference](https://github.com/Knuckles-Team/pipelines/blob/main/reference/delivery-practice.md) for waiting, branches, merge holds, worktree safety and verification. The [constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) holds the binding articles: XXVIII (merges and releases), XXIX (checks tell the truth), XVIII (landed means reachable) and XXV (small units).

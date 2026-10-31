---
mode: append
---
## Outputs and gates

Run `pipelines-hook spec-standard` first and treat its findings as the baseline: a row with no task line, a task naming no row, a behavior row with neither a bound test nor a test-spec entry, an orphan `FR-` or `SC-` label, an open clarification marker. Write `specs/<stable-id>/checklists/analysis.md` (lower case; plain bullets, no unchecked task boxes) with requirement-to-task-to-test coverage and end it with **Pass**, **Fail** or **Needs revision** and a coverage fraction. Fill `specs/<stable-id>/checklists/requirements.md` from the pipelines `specs/_template/checklists/requirements.md`; an unchecked item fails the gate. Report an unavailable tool or undefined threshold as a gap, never as a pass.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

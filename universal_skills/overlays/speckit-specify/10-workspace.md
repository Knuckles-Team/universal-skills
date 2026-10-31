---
mode: append
---
## Intake and row output

- Collect these inputs before writing; recommend a default for each and accept an empty answer: feature name (2 to 100 characters), owning domain, goal, key constraints, expected inputs, expected outputs.
- Write `specs/<stable-id>/spec.md` and the `requirements.md` rows. The spec has prioritized user stories (`### User Story N - <title> (Priority: P1)`) with Given/When/Then scenarios, Edge Cases, Assumptions and out-of-scope items. Number functional requirements `FR-001` and success criteria `SC-001`; each label names the `-R` rows it maps to.
- Each row states one verifiable behavior and its proving test. Creating a spec never marks a row landed.
- Put an unresolved question in the spec as `[NEEDS CLARIFICATION: <question>]` with its effect on implementation.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

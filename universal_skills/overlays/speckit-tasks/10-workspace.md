---
mode: append
---
## Task line format

Write each task as `- [ ] T001 [P] [US1] <ROW-ID> description`. The task number and the requirement row ID are required; `[P]` and `[US1]` are optional. Every active row needs a task line and every task names an existing row; `pipelines-hook spec-standard` fails a touched spec that breaks either rule. Include tasks that reuse the named wiring, add positive and negative tests bound to the rows, verify the runtime path, and update the affected docs. Add a final evidence task that reconciles the rows against merged code, tests and documentation. Cross-repository work gets local tasks in each owning repository with links to the contract.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

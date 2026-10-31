---
mode: append
---
## Constitution content

Create `.specify/memory/constitution.md` from `.specify/templates/constitution-template.md`: one page that links the organization constitution and standards by public URL and adds only principles specific to this repository. Run `pipelines-hook spec-standard`; its constitution check passes once the file exists.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

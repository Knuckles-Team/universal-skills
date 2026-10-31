---
mode: append
---
## Plan sections

`plan.md` follows `.specify/templates/plan-template.md`: Summary, Technical Context, Constitution Check (pass, or justify each failure under Complexity Tracking), Project Structure, Phase 0 to 2, Build contract, Production caller chain and Cross-repo seams. Name the existing components and wiring to reuse, the interfaces and data flows, migration and failure handling, and the cross-repository contracts. Add `research.md`, `data-model.md`, `contracts/` and `quickstart.md` where the plan calls for them.

## Workspace conventions

- Feature artifacts live in tracked repository-root `specs/<stable-id>/`, never under `.specify/specs/` or `agent_data/`. `.specify/` holds only project configuration, templates and `.specify/memory/constitution.md`.
- Route the feature first with the ecosystem boundaries standard (https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md). Each behavior has one normative owner. Look up the owning spec and extend it before you add a new one.
- Keep every requirement row ID (`<PREFIX>-<AREA>-R012.4`), every `Spec:` commit trailer and every test binding intact. The delivery state (`SPECIFIED`, `LANDED`, `VERIFIED`, `RETIRED`) is computed by `pipelines-hook spec-status`; never write a `Status:` line or `status.json`.
- Specs and prompts name no private repository, internal host, homelab inventory or local workspace path. A contributor with only public GitHub access must be able to complete the work.
- When `.specify/scripts/` is absent, derive the feature directory from the repository root and the stable ID instead of running a script.

### Optional artifacts

Add each optional artifact only where it carries content, and the analysis check requires it there: `contracts/` holds one human-written `.md` contract per cross-repo seam (wire shape, refusal codes, and `Provider:` and `Consumer:` lines that name the row IDs on both sides; no generated contract); `data-model.md` when a row names new types, ontology classes or tables; `quickstart.md` when a row is a `served` behaviour row, naming the scenario or test command that runs its proof; `research.md` only when Phase 0 lists unknowns. File and directory names are lower-case kebab-case; plans live only in `specs/<family>/plan.md`, templates only in `.specify/templates/`, the constitution only in `.specify/memory/`. `checklists/requirements.md` is filled before landing.

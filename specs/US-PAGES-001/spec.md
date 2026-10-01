# US-PAGES-001: Consolidate published documentation

**Delivery:** SPECIFIED

**Acceptance:** NOT_AUDITED

**Owner:** universal-skills

**Source of truth:** this tracked spec package. The [organization spec report](https://knuckles-team.github.io/.github/spec-status.html) is an index, not acceptance authority.
Every requirement ID this spec owns is defined in [requirements.md](requirements.md); delivery
state and evidence for each ID are recorded in `status.json`.

## Goal

Make GitHub Pages the readable view of this repository's skill catalog,
contribution workflow, and relevant specifications while keeping all editable
sources tracked in Git. `docs/` currently supplies the MkDocs Pages build and
must remain until a replacement build reads another tracked source.

## Users and acceptance scenarios

1. A contributor can follow Pages navigation to the contribution guide and the public `spec-generator`, `task-planner`, `spec-verifier`, and `sdd-full-lifecycle` skill sources.
2. A maintainer edits one canonical tracked file and sees the change after Pages builds, without updating a duplicate.
3. A spec reader sees a stable ID, owner, separate delivery and acceptance states, related public specs, and acceptance receipts when available; open work is visibly open.
4. A cloud PR author runs required checks from a clean checkout with fixtures or disposable dependencies.
5. An existing reader can still reach catalog, architecture, and roadmap URLs or redirects.

## Requirements

1. Publish contributor instructions and links to the repository's universal
   Spec Kit skills from the Pages navigation.
2. Define one canonical source for each document and render or link it into
   Pages without maintaining divergent copies.
3. Link each published spec to its stable ID, owning repository, implementation
   status, related specs, and acceptance evidence when available.
4. Keep provider deployment documentation in the owning provider repository;
   universal-skills CI must not require generated edits in sibling repositories.
5. Preserve existing catalog, architecture, and roadmap content and their URLs
   or provide working redirects when changing the site layout.
6. Keep required cloud PR checks hermetic or self-provisioning. Report
   credentialed and live-environment checks separately after merge or on a
   schedule without weakening required correctness and quality checks.

These are `US-PAGES-001-FR1` through `US-PAGES-001-FR6` in order. Evidence for FR1 is the built nav and link check; FR2 is a source-to-render test; FR3 is open/accepted render fixtures; FR4 and FR6 require a clean-checkout CI run; FR5 requires a deployed URL inventory.

## Design and reuse

Reuse `mkdocs.yml`, `.github/workflows/pages.yml`, and the shared
`Knuckles-Team/pipelines` Pages workflow. The initial change adds a Pages
contribution entry and removes the cross-repository README freshness hook.
Before moving any source, inventory current links and choose a build-time
inclusion or link approach that gives each page one canonical Git file.
Keep `specs/` as the reviewable source for build contracts; Pages is a rendered
view, not the authority for completion.

The current `docs/contributing.md` link and removal of the sibling README freshness hook are partial groundwork. `specs/<id>/status.json` supplies the local delivery and acceptance states. The [organization hub governance spec](https://github.com/Knuckles-Team/.github/tree/main/specs/crossrepo-authority-governance) owns cross-repository indexing; [pipelines](https://github.com/Knuckles-Team/pipelines) owns the shared Pages workflow. This repository owns its invocation and site output. Do not publish private planning documents, internal infrastructure or cluster inventory, or local filesystem paths.

Use the configured pre-commit quality checks and reuse the existing MkDocs and workflow wiring. CCCC, `jscpd`, and Dupehound have no configured threshold in this site's current path; identify a real command and threshold before claiming a pass. Reject acceptance claims without exact merged-code and passing-test evidence.

## Acceptance and tests

- A Pages build includes the contribution entry and resolves its internal links.
- Existing catalog and architecture pages remain reachable after deployment.
- Editing a canonical document updates its published view without a manual copy.
- `pre-commit run --all-files` passes without inspecting sibling provider READMEs.
- A spec marked complete links a merged implementation and passing acceptance
  evidence; a planned spec is visibly marked planned.

## Open work

- Select and implement the canonical-source inclusion method for root guides
  and tracked specs.
- Add a Pages build/link check to CI, then deploy and verify published URLs.
- Review ecosystem repository templates so each project can publish its own
  specs through the same pattern.

## Boundaries

Provider deployment docs stay in their owning repositories. A Pages publication does not prove implementation. Keep `docs/` until a replacement tracked source is wired and deployed. No other repository must adopt a mandatory `/docs` directory or documentation freshness gate.

See `plan.md`, `test-spec.md`, `tasks.md`, and `status.json` for design, verification, work, and current state.

# US-PAGES — Consolidate published documentation

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

## User scenarios and testing

### User Story 1 - Read the catalog, guide and specs on one site (Priority: P1)

A contributor or reader opens the Pages site to find the skill catalog, the contribution guide and the specifications, so that one site answers where things are and what state they are in.

**Acceptance scenarios**

1. Given the built site, When a contributor follows the navigation, Then the contribution guide and the four spec-workflow skill sources open and every internal link resolves.
2. Given a canonical tracked file, When a maintainer edits it and the site rebuilds, Then the published page changes with no second copy to update.
3. Given an open spec and a synthetic accepted fixture, When a reader opens each, Then the open one shows pending evidence and the accepted one shows exact merged-code and test links.

### User Story 2 - Move between sites without relearning the layout (Priority: P2)

A reader who knows another ecosystem documentation site finds the same navigation and content hierarchy here.

**Acceptance scenarios**

1. Given the shared Pages template, When the cross-site check compares this repository's navigation, Then the hierarchy matches the template.

## Edge Cases

- A missing source file, a broken internal link, an invalid status or an absent redirect fails the build with the affected path.
- A status file that is absent still builds, and the page shows the evidence as open.
- An old catalog, architecture or roadmap URL still returns content or a working redirect.

## Assumptions

- The shared pipelines Pages workflow keeps its public contract.
- Provider deployment documentation stays in the owning provider repository.
- Live URL smoke checks run after merge or on a schedule and are reported separately.

## Users and acceptance scenarios

1. A contributor can follow Pages navigation to the contribution guide and the public `speckit-specify`, `speckit-tasks`, `speckit-analyze`, and `sdd-full-lifecycle` skill sources.
2. A maintainer edits one canonical tracked file and sees the change after Pages builds, without updating a duplicate.
3. A spec reader sees a stable ID, owner, separate delivery and acceptance states, related public specs, and acceptance receipts when available; open work is visibly open.
4. A cloud PR author runs required checks from a clean checkout with fixtures or disposable dependencies.
5. An existing reader can still reach catalog, architecture, and roadmap URLs or redirects.

## Requirements

1. Publish contributor instructions and links to the repository's universal
   spec-workflow skills from the Pages navigation.
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

These are requirements FR1 through FR6 in order. Evidence for FR1 is the built nav and link check; FR2 is a source-to-render test; FR3 is open/accepted render fixtures; FR4 and FR6 require a clean-checkout CI run; FR5 requires a deployed URL inventory.

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

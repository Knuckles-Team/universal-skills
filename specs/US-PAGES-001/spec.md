# US-PAGES-001: Consolidate published documentation

**Status:** planned

**Owner:** universal-skills

**Source:** ecosystem documentation and specification program

## Goal

Make GitHub Pages the readable view of this repository's skill catalog,
contribution workflow, and relevant specifications while keeping all editable
sources tracked in Git. `docs/` currently supplies the MkDocs Pages build and
must remain until a replacement build reads another tracked source.

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

## Design and reuse

Reuse `mkdocs.yml`, `.github/workflows/pages.yml`, and the shared
`Knuckles-Team/pipelines` Pages workflow. The initial change adds a Pages
contribution entry and removes the cross-repository README freshness hook.
Before moving any source, inventory current links and choose a build-time
inclusion or link approach that gives each page one canonical Git file.
Keep `specs/` as the reviewable source for build contracts; Pages is a rendered
view, not the authority for completion.

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

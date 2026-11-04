# US-PAGES — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

GitHub Pages is the readable view of the skill catalog, the contribution guide and the specifications, and every page comes from one tracked file. The live caller is the Pages workflow (.github/workflows/pages.yml:13) building MkDocs with the hook `on_files` (scripts/pages_sources.py:118). The reuse candidates are MkDocs `File.generated` and the shared pipelines Pages workflow.

## Technical Context

- **Language/Version**: Python 3.14 standard, 3.12 floor (requires-python >=3.12)
- **Primary Dependencies**: MkDocs with the in-repository hook scripts/pages_sources.py; the shared pipelines Pages workflow
- **Storage**: N/A
- **Testing**: pytest (`uv run pytest`) with the tests named in the rows
- **Target Platform**: Linux, macOS and Windows developer machines and CI
- **Project Type**: skill library
- **Performance Goals**: N/A
- **Constraints**: One canonical tracked file per page, hermetic PR checks, existing public URLs preserved, no secret needed to render
- **Scale/Scope**: 2 active rows; 5 existing public routes and the spec package pages

## Constitution Check

- I One owner per concept: pass. Each row names one owning file.
- II Extend before you create: pass. Each `Shape:` sentence names the helper to reuse.
- XXIV Complete rows: pass. Every active row holds a caller chain, a shape and a test reference.
- XI Code stays small: pass. The Build contract lists the complexity and size limits.
- XXI Public files stay portable: pass. The spec holds no host data and no local path.
- R-I A skill is atomic and portable: pass. Each skill does one job with portable frontmatter.
- R-II Paths are legal on every platform: pass. New paths stay within the length limits.

## Project Structure

Existing paths this spec owns:

```text
mkdocs.yml                      existing  navigation and hook list
scripts/pages_sources.py        existing  in-memory page generation from tracked files
CONTRIBUTING.md                 existing  contribution guide and URL inventory
docs/                           existing  catalog, architecture and roadmap pages
tests/pages_contracts.py        existing  offline Pages contract tests
.github/workflows/pages.yml     existing  caller of the shared Pages workflow
specs/pages/                    existing  the public spec package
```

## Phase 0: Research

No unknowns. The build path, the hook and the contract tests are known; this spec adds no research.md.

## Phase 1: Design

Pages is a rendered view and never the authority for completion. The sections below keep the existing design notes.

### US-PAGES design plan

### Existing architecture

`docs/*.md` feeds MkDocs via `mkdocs.yml`. `.github/workflows/pages.yml` invokes `Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main` on version tag pushes (`v*`) and manual dispatch. Root `CONTRIBUTING.md` and `specs/` are tracked sources outside the current MkDocs tree. The organization hub indexes public specs across repositories.

### Design to implement

Inventory existing Pages URLs and map every rendered page to one tracked source. Choose build-time inclusion or direct linking for root guides and specs; document that choice in the implementation PR. Do not create manually synchronized copies. Keep old catalog, architecture, and roadmap URLs until redirects are deployed and tested.

Render spec entries from local `specs/<id>/status.json` with stable ID, owner, separate delivery and acceptance, related public specs, and exact merged implementation/test receipts when accepted. Show pending evidence explicitly for open specs. Pages and the org report are views of owner-native status.

Expand Pages path triggers for every canonical source affecting output. Reuse the shared workflow; change its public contract in pipelines only if the selected source method requires it. Required PR checks should build and check links with fixtures or disposable dependencies. Live deployment smoke checks run separately after merge or on a schedule.

### Failure and compatibility

A missing source, broken link, invalid status, or absent redirect should fail a local check with path and cause. Rendering needs no secret. A failed deployment reports the workflow run; it does not silently change acceptance. Use the existing MkDocs wiring and avoid a second renderer unless the selected approach needs one.

### Implemented draft slice

Native MkDocs `on_files` hooks generate the existing `/contributing/` view from
root `CONTRIBUTING.md` and explicitly publish this public spec package in memory.
No manual copies or new rendering engine are introduced. The canonical-source
and URL inventory is in `CONTRIBUTING.md`; all five existing routes stay intact.
Local repository links are checked before rebasing to public GitHub sources;
package links stay within the rendered spec. Strict MkDocs validates local
page and anchor targets. Delivery and acceptance are rendered independently from
`status.json`, with open evidence explicit and accepted receipt shape checked.
The rendered spec headline metadata also comes from `status.json`, so a canonical
status edit cannot leave contradictory delivery or acceptance claims on Pages.

The dedicated Pages check workflow builds on PRs with read-only permissions and
only this checkout plus pinned disposable documentation dependencies. It runs
`tests/pages_contracts.py` explicitly, separately from the package's locked
pre-commit/test environment. Main deployment still uses the existing shared
Pages workflow and now watches canonical guide, spec, and hook changes.
No change enables deployment or claims accepted status. Live URL checks,
receipt authenticity audits, and cross-repository template adoption remain open.

## Phase 2: Task approach

Order the work producer first: the canonical-source inventory and hook, then the contract tests, then the shared-template alignment (R001). Each task line in tasks.md names one row.

## Complexity Tracking

None. The constitution check passed with no violation.

## Build contract

The change must meet these gate thresholds from the organization constitution table.

- Cyclomatic complexity 10 and cognitive complexity 15 per function (`pipelines_hooks/complexity`).
- Words per sentence 20 (`ste`).
- Clone similarity 0.85 blocking at 40 tokens (`dupehound`).
- KISS limits from `.config/kiss.toml`: 35 statements, 15 locals, 20 calls, 3 positional arguments, 4 indentation levels, 300 lines and 10 functions per file.
- Pre-land fast set: `format`, `hygiene`, `secrets`, `types`, `tests-fast`; post-land set: `spec`, `tests`, `supply-chain`.

Repository commands: `uv run pytest` for the tests named in the rows and `pre-commit run --all-files` for ruff, mypy, vulture, codespell and bandit.

No scanner gaming, no suppression and no duplicate implementation: a row reuses the helper named in its `Shape:` sentence.

Pages contract tests run with `python -m pytest tests/pages_contracts.py -q` (as in .github/workflows/ci.yml).

## Production caller chain

Entry point: a `v*` tag push or a manual dispatch starts .github/workflows/pages.yml:13, which calls the shared `pages_pipeline.yml`; MkDocs loads the hook `on_files` (scripts/pages_sources.py:118), which generates the contribution and spec pages from tracked files. Obsolete paths to delete: none.

## Cross-repo seams

None. The shared Pages workflow is owned by pipelines and is called unchanged.

# US-PAGES-001 design plan

## Existing architecture

`docs/*.md` feeds MkDocs via `mkdocs.yml`. `.github/workflows/pages.yml` invokes `Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main` on main changes to `docs/**`, `mkdocs.yml`, or `README.md`. Root `CONTRIBUTING.md` and `specs/` are tracked sources outside the current MkDocs tree. The organization hub indexes public specs across repositories.

## Design to implement

Inventory existing Pages URLs and map every rendered page to one tracked source. Choose build-time inclusion or direct linking for root guides and specs; document that choice in the implementation PR. Do not create manually synchronized copies. Keep old catalog, architecture, and roadmap URLs until redirects are deployed and tested.

Render spec entries from local `specs/<id>/status.json` with stable ID, owner, separate delivery and acceptance, related public specs, and exact merged implementation/test receipts when accepted. Show pending evidence explicitly for open specs. Pages and the org report are views of owner-native status.

Expand Pages path triggers for every canonical source affecting output. Reuse the shared workflow; change its public contract in pipelines only if the selected source method requires it. Required PR checks should build and check links with fixtures or disposable dependencies. Live deployment smoke checks run separately after merge or on a schedule.

## Failure and compatibility

A missing source, broken link, invalid status, or absent redirect should fail a local check with path and cause. Rendering needs no secret. A failed deployment reports the workflow run; it does not silently change acceptance. Use the existing MkDocs wiring and avoid a second renderer unless the selected approach needs one.

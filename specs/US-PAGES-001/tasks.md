# US-PAGES-001 work items

- [x] Add Pages contribution navigation and public Spec Kit links.
- [x] Remove sibling provider README freshness dependency from universal-skills checks.
- [x] Inventory Pages URLs and declare one tracked source for each page.
- [x] Implement build-time inclusion or direct links for root guides and specs.
- [x] Render stable spec IDs with separate delivery and acceptance states and public receipts.
- [x] Add deterministic Pages build, link, metadata, and negative-case checks to PR CI.
- [x] Update workflow triggers for all sources that affect output.
- [ ] Deploy and verify old URLs, redirects, and contribution/skill links.
- [ ] Review public repository template pattern with owner repositories.
- [ ] Audit merged implementation and test receipts before changing status.

Checkboxes show task progress only; they do not prove acceptance.

No task above cites a `requirements.md` ID by name. `US-PAGES-001` (consolidate published
documentation) is closed by the tasks above. `US-PAGES-R001` (shared documentation hierarchy
across the fleet's sites) is not yet covered by an existing task:

- [ ] Align this repository's published navigation and content hierarchy (catalog, contribution
      guide, specs) with the shared Pages template and workflow used by the other core ecosystem
      repositories' documentation sites, and add a cross-site navigation/link-structure check.
      Closes `US-PAGES-R001`.

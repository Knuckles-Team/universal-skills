# US-PAGES-001 requirements

Every requirement this specification owns, with the proof that closes it. Delivery state and
public evidence for each ID are recorded in [`status.json`](status.json); this file defines what
each ID means. The design is in [`spec.md`](spec.md) and [`plan.md`](plan.md), the test contract
in [`test-spec.md`](test-spec.md), and the work order in [`tasks.md`](tasks.md).

| ID | Requirement | Verification |
|---|---|---|
| `US-PAGES-001` | **Consolidate published documentation.** GitHub Pages serves as the readable view of this repository's skill catalog, contribution workflow, and relevant specifications, while every page's content stays sourced from one canonical tracked file in Git rather than a duplicated copy. | A Pages build check confirms the navigation's internal links resolve and that editing the canonical tracked document updates the published view without a manual copy. |
| `US-PAGES-R001` | **Shared documentation hierarchy across the fleet's sites.** universal-skills' published skill catalog and specifications follow the same reusable navigation and content hierarchy, assembled from the shared Pages template and workflow, used by the documentation sites of the other core ecosystem repositories, so a reader moving between them finds the same structure. | A cross-site navigation and link-structure check confirms this repository's published hierarchy matches the shared template used across the fleet's documentation sites. |

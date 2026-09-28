# US-PAGES-001 test specification

Use one real open spec and a synthetic accepted fixture with exact merged-code and passing-test receipts. Never mark a real spec accepted to satisfy a fixture. Record the existing catalog, architecture, and roadmap URLs before layout changes.

| Scenario | Requirements | Expected result and evidence |
| --- | --- | --- |
| Contribution navigation | FR1 | Pages build exposes guide and four skill links; CI link check resolves each. |
| Canonical edit | FR2 | A fixture edit changes output on rebuild without a maintained copy. |
| Open and accepted status | FR3 | Open entry shows pending evidence; accepted fixture has exact merged-code/test links; missing receipts fail validation. |
| Checkout isolation | FR4, FR6 | Required checks run with only this checkout and disposable dependencies; no sibling README or private service. |
| URL compatibility | FR5 | Deployed old URLs return content or working redirects; record HTTP smoke result. |
| Negative cases | FR2, FR3, FR5 | Missing source, broken internal link, invalid status, or absent redirect fails with affected path. |
| Live deployment | FR5, FR6 | Post-merge or scheduled Pages run reports deployed URL smoke separately. |

Run `pre-commit run --all-files` for configured repository quality. For added code, run focused tests and configured CCCC/`jscpd`/Dupehound checks if present. Record absent commands or thresholds; do not claim a pass. Accepted status requires verified merged implementation and passing acceptance evidence.

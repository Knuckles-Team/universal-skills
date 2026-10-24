# US-WEB-RESEARCH — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `US-WEB-RESEARCH-R001` | **The web-crawler skill is a thin skill over `research.web` (rollup).** No skill named `web-scraper` exists. The `web-crawler` skill is the page scraper of this repository. It must call the arbora operation `research.web` (`ARBORA-OPS-R067`). It must hold no page fetch, render, crawl or extraction code. Children `.1` to `.5` deliver it. | See each child. |
| `US-WEB-RESEARCH-R001.1` | **Call the operation.** `universal_skills/skills/web-crawler/scripts/crawl.py` must call `research.web` through `arbora.client`. A `--query` argument maps to `query`. A `--urls` argument maps to `urls`. `--backend` maps to `backend`. The script prints the Document IDs with their citations. Proving test: `tests/test_web_research_skill.py::test_crawl_calls_research_web`. | One script run sends one `research.web` call with the mapped arguments. |
| `US-WEB-RESEARCH-R001.2` | **Delete local scraping.** The skill must delete the HTTP, browser, `robots.txt`, sitemap and markdown code in `crawl.py` and `scripts/security_runtime.py`. `SKILL.md` must describe only the operation call. Proving test: `tests/test_web_research_skill.py::test_skill_has_no_http_client`. | The test finds no HTTP client, browser driver or HTML parser import in the skill scripts. |
| `US-WEB-RESEARCH-R001.3` | **Alias.** The `web-fetch` skill must forward to `web-crawler` with one URL and `max_pages` 1. It must hold no code of its own beyond the forward. Proving test: `tests/test_web_research_skill.py::test_web_fetch_forwards`. | A `web-fetch` run sends one `research.web` call with one URL. |
| `US-WEB-RESEARCH-R001.4` | **Refusal.** The skill must print the refusal code of the operation and exit with status 2. It must not fall back to a local fetch. Proving test: `tests/test_web_research_skill.py::test_refusal_exits_without_fallback`. | A refused call exits 2 and makes no other network call. |
| `US-WEB-RESEARCH-R001.5` | **Hot-path proof.** The test runs `crawl.py` against a fixture arbora server that serves `research.web`. It denies every other network destination. Proving test: `tests/test_web_research_skill_served.py::test_skill_reaches_research_web_only`. | The fixture receives one call, and the skill makes no other network request. |

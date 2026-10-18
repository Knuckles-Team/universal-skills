# US-WEB-RESEARCH — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `US-WEB-RESEARCH-R001` | Every child row. | See each child. |
| T-002 | `US-WEB-RESEARCH-R001.1` | `tests/test_web_research_skill.py::test_crawl_calls_research_web` | One script run sends one `research.web` call with the mapped arguments. |
| T-003 | `US-WEB-RESEARCH-R001.2` | `tests/test_web_research_skill.py::test_skill_has_no_http_client` | The test finds no HTTP client, browser driver or HTML parser import in the skill scripts. |
| T-004 | `US-WEB-RESEARCH-R001.3` | `tests/test_web_research_skill.py::test_web_fetch_forwards` | A `web-fetch` run sends one `research.web` call with one URL. |
| T-005 | `US-WEB-RESEARCH-R001.4` | `tests/test_web_research_skill.py::test_refusal_exits_without_fallback` | A refused call exits 2 and makes no other network call. |
| T-006 | `US-WEB-RESEARCH-R001.5` | `tests/test_web_research_skill_served.py::test_skill_reaches_research_web_only` | The fixture receives one call, and the skill makes no other network request. |

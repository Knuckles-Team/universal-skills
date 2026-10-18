---
name: web-crawler
domain: research
skill_type: skill
description: >-
  Research the web through the Arbora research.web operation: search, select,
  fetch, ingest and cite pages. Use when a task needs web pages as cited
  Documents in the knowledge graph. The skill holds no fetch or crawl code.
tags: [web, research, fetch, arbora, ingest, citations]
license: MIT
metadata:
  version: '1.3.11'
  author: Repository Maintainers
---
# Web Crawler Skill

`scripts/crawl.py` sends one `research.web` call to Arbora and prints the
Document IDs with their citations. It fetches nothing itself.

Arbora runs the whole pipeline behind that one governed operation: web search,
page selection, fetching through the webarchiver connector (ArchiveBox when
webarchiver fails on a page), `SourceIngest`, enrichment and citations.

## Usage

```bash
export ARBORA_URL=https://arbora.example   # the gateway origin
export ARBORA_TOKEN=...                    # a bearer token with ingest:write
python scripts/crawl.py --query "kubernetes pod disruption budget"
python scripts/crawl.py --urls https://example.org/a https://example.org/b
python scripts/crawl.py --query "..." --backend archivebox --max-pages 3
```

| Argument | `research.web` param |
|---|---|
| `--query` | `query` |
| `--urls` | `urls` (1 to 32) |
| `--backend` | `backend` (`webarchiver` or `archivebox`) |
| `--max-pages` | `max_pages` (1 to 32) |

## Output and refusals

Success prints JSON with `state` and `documents`; each document has its
`document_id` and `citations` (URL, retrieval time, content digest, backend,
query and rank). A refused call prints `{"refused": "<code>"}` to stderr and
exits with status 2. There is no local fallback.

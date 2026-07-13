---
name: web-crawler
domain: research
skill_type: skill
description: >-
  Comprehensive tool for crawling websites, single pages, and sitemaps to yield
  clean, refined markdown that is natively ingested into the epistemic-graph
  Knowledge Graph (graph-os) as Document+Chunk+Concept objects with provenance,
  by default. Use when the agent needs to read or extract knowledge from online
  documentation, parse entire websites recursively, extract markdown from a
  single URL, chunk markdown, bulk-process URLs from a sitemap XML, or persist
  scraped web content into the Knowledge Graph for later semantic search/recall.
license: MIT
tags: [web, crawler, documentation, docs, scrapper, scrape, extract, markdown, sitemap, knowledge-graph, graph-os, ingest]
metadata:
  version: '1.2.0'
  author: Genius
---
# Web Crawler Skill

This skill provides a robust CLI script (`scripts/crawl.py`) that utilizes `crawl4ai` to scrape websites, chunk markdown, process sitemaps, and recursively extract pages — and, **by default, ingests every crawled page into the epistemic-graph Knowledge Graph** via graph-os's unified `ingest_url` pipeline. It is a **thin entrypoint**: crawling/discovery lives here, but the actual fetch-quality decision, chunking, contextual enrichment, embeddings, concept extraction, and provenance stamping all happen in the ONE shared ingestion path (`agent_utilities.knowledge_graph.ingestion`) that every URL source (web-crawler, ArchiveBox, search results, feeds) converges on — this skill does not maintain a parallel ingestion mechanism.

## Usage

Use the provided `scripts/crawl.py` to extract text from websites. Always consider if you need to output to a file or stdout. For single pages, stdout is fine. For sitemaps and recursive crawls, always specify `--output-dir`.

```bash
python scripts/crawl.py --urls <url> --strategy <strategy> [options]
```

### Strategies

1. **`single`**: Crawls a single page.
   * `python scripts/crawl.py --urls https://example.com/page --strategy single`
2. **`chunked`**: Crawls a single page and splits the markdown by H1/H2 headers (# or ##).
   * `python scripts/crawl.py --urls https://example.com/page --strategy chunked`
3. **`sitemap-sequential`**: Fetches all URLs in a `sitemap.xml` and crawls them one by one, reusing the browser session. Best for small numbers of URLs when you need reliable parsing without taxing the target server.
   * `python scripts/crawl.py --urls https://example.com/sitemap.xml --strategy sitemap-sequential --output-dir ./docs`
4. **`sitemap-parallel`**: Fetches all URLs in a `sitemap.xml` and crawls them concurrently (memory adaptive dispatch). Best for large documentation sites.
   * `python scripts/crawl.py --urls https://example.com/sitemap.xml --strategy sitemap-parallel --max-concurrent 10 --output-dir ./docs`
5. **`recursive`**: Crawls a site starting from a single URL and recursively follows internal links up to a depth limit, deduplicating URLs. Automatically enforces path prefix restriction to stay within the starting section.
   * `python scripts/crawl.py --urls https://example.com/docs/ --strategy recursive --max-depth 2 --output-dir ./crawled_content`

> [!TIP]
> **Sitemap Auto-Discovery**: If you provide a single URL and use the `single` or `recursive` strategy, the script will automatically check `robots.txt` and `/sitemap.xml`. If a sitemap is found, it will switch to `sitemap-parallel` for complete and efficient coverage.

### Options

* `--max-depth`: Max recursion depth for `recursive` (default: 3).
* `--max-concurrent`: Number of parallel browser sessions for `sitemap-parallel` and `recursive` (default: 10).
* `--max-pages`: Total page limit for recursive crawls (default: 500).
* `--output-dir`: Important! Directory to save markdown files.
* `--disable-magic-js`: Use if you don't want the heavy element-scrubbing CSS/JS to run (good for clean static sites).
* `--ignore-prefix-restriction`: Disables the automatic path-prefix filter in recursive mode.
* `--wait-for`: Custom CSS selector or JS expression to wait for (e.g., `"css:.my-content"`).
* `--insecure`: Disable SSL verification (use with caution).
* `--no-kg-ingest`: Disable native Knowledge Graph ingestion (see below). File output (`--output-dir`) is unaffected either way.
* `--kg-endpoint`: graph-os gateway base URL for ingestion (else `$GRAPH_OS_URL`, default `http://graph-os.arpa`).

## Knowledge Graph Ingestion (native, default ON)

**Every crawl ends in the epistemic-graph, not just files.** As each page is
successfully crawled and cleaned, the skill submits it to graph-os's unified
`ingest_url` pipeline — the same `graph_ingest action=ingest_url` MCP tool /
`POST /api/graph/ingest {"action":"ingest_url","target_path":<url>}` REST call
an agent would use directly. graph-os re-resolves the URL through its own
fetch chain (ArchiveBox → crawl4ai → requests) and materializes:

* a **`:Document`** node — verbatim content, `source_url`, `content_hash`
  (`ast_hash`), `fetch_backend` (which resolver served it), `fetched_at`
  (crawl timestamp), and `source_system`/`domain` stamped `"web"`;
* **`:Concept`** nodes + linking edges — LLM-extracted, context-derived
  entities/topics from the page (on by default, not just flat text);
* **`:Chunk`** objects with embeddings + contextual-retrieval enrichment
  (default ON for `ingest_url`, at parity with connector ingestion), for
  semantic search over the page.

Re-ingesting the same URL is idempotent/delta — the Document id is derived
from `source_url` + a content hash, so an unchanged page is a no-op and a
changed one updates in place.

### Clean & refined markdown (what actually lands in the KG)

`extract_markdown()` prefers crawl4ai's **`fit_markdown`** (the
`PruningContentFilter`-scored, boilerplate-stripped rendering — nav/sidebar/
cookie-banner/footer chrome scored out) over the unfiltered `raw_markdown`,
then collapses incidental whitespace. Across a multi-page crawl
(`sitemap-*`/`recursive`), a normalized content fingerprint dedups
near-identical pages (e.g. print views, redirects landing on the same
content) — a duplicate is logged and skipped, never saved or ingested twice.

### Degradation

If graph-os is unreachable (network error, gateway down), the first failed
submission logs a clear warning and the run **falls back to file-only
output** for the remainder of the crawl — it never blocks or fails the crawl
itself. Check the final `KG ingestion: N page(s) submitted to <endpoint>`
summary line to confirm ingestion happened.

### Internal use as an acquisition backend

`agent-utilities` itself drives this script as a subprocess for two internal
paths — a single-page fetch backend (`web_fetch._fetch_via_crawl4ai`, behind
`ingest_url`'s own resolver) and the skill-graph corpus builder
(`skill_graph_pipeline._crawl_via_script`). Both always pass `--no-kg-ingest`
(they run their own, differently-scoped ingestion afterward) — this is why
`--no-kg-ingest` exists as an explicit opt-out rather than the default.

### Querying it back

```
graph_search query="<topic from the crawled page>"
graph_query cypher="MATCH (d:Document {source_url: '<url>'}) RETURN d"
```

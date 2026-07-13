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
* `--kg-mode`: `content` (default) or `url` — how each page is ingested (see below).
* `--kg-endpoint`: graph-os base URL for ingestion (else `$GRAPH_OS_URL`, default `http://graph-os.arpa`); `/mcp` is appended automatically. `$GRAPH_OS_TOKEN` supplies a bearer token if the gateway requires auth.

## Knowledge Graph Ingestion (native, default ON)

**Every crawl ends in the epistemic-graph, not just files.** As each page is
successfully crawled, cleaned, and deduped, the skill ingests it into graph-os /
epistemic-graph **over graph-os's MCP streamable-http surface** (`<endpoint>/mcp`
— a JSON-RPC `tools/call` after an `initialize` handshake, mounting the tool with
`load_tools` since graph-os is a dynamic multiplexer). This is exactly how the
platform reaches the fleet — no REST gateway required, stdlib `urllib` only.
There are two native modes:

**`content` mode (default) — push the crawler's own cleaned markdown.** The
skill calls the `document_process` tool with the page's refined `fit_markdown`
(`document=<md>`, `source=<url>`). graph-os chunks, embeds, and contextually
enriches **our cleaned content** into a `:Document` + `:Chunk` objects with a
`content_hash`, `source` = the page URL, and the title taken from the page's
first `#` heading. This is the mode that **guarantees the clean, refined
markdown is what lands in the KG** — the content is fixed by *this* crawler's
crawl4ai `fit_markdown`, independent of whatever fetch backend the graph-os pod
itself has. This directly fulfills "ingest a clean and refined set of markdown
scraped documents".

**`url` mode (`--kg-mode url`) — delegate the fetch.** The skill calls the
`graph_ingest` tool with `action='ingest_url', target_path=<url>`. graph-os
**re-fetches** through its own resolver chain (ArchiveBox → crawl4ai → requests)
and materializes a `:Document` (`source_url`/`ast_hash`) **plus `:Concept` nodes**
(LLM entity/topic extraction) and chunks. Prefer this when you want graph-os's
ArchiveBox snapshot / server-side fetch and its concept graph — but note the KG
content is only as clean as the gateway pod's fetch backend (if that pod lacks
crawl4ai it falls back to `requests+markitdown`, which keeps more page chrome).

Re-ingesting the same page is idempotent — the Document id / `content_hash`
is derived from the content, so an unchanged page is a no-op and a changed one
updates in place.

### Clean & refined markdown (what actually lands in the KG)

`extract_markdown()` prefers crawl4ai's **`fit_markdown`** (the
`PruningContentFilter`-scored, boilerplate-stripped rendering — nav/sidebar/
cookie-banner/footer chrome scored out) over the unfiltered `raw_markdown`,
then collapses incidental whitespace. Across a multi-page crawl
(`sitemap-*`/`recursive`), a normalized content fingerprint dedups
near-identical pages (e.g. print views, redirects landing on the same
content) — a duplicate is logged and skipped, never saved or ingested twice.
In the default `content` mode this cleaned markdown is exactly what is pushed
to the KG.

### Degradation

If graph-os is unreachable (network error, gateway down), the first failed
submission logs a clear warning and the run **falls back to file-only
output** for the remainder of the crawl — it never blocks or fails the crawl
itself. (If a page reaches only the plain-HTTP fallback fetch and thus has no
clean markdown, `content` mode transparently degrades to `url` mode for that
page so graph-os can still fetch it server-side.) Check the final
`KG ingestion (<mode>): N page(s) submitted to <endpoint>` summary line to
confirm ingestion happened.

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
# content mode stamps the page URL on d.source; url mode on d.source_url:
graph_query cypher="MATCH (d:Document) WHERE d.source = '<url>' OR d.source_url = '<url>' RETURN d"
graph_query cypher="MATCH (c:Chunk)-[:CHUNK_OF]->(d:Document) WHERE d.source = '<url>' RETURN c"
```

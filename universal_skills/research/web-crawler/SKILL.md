---
name: web-crawler
description: >-
  Comprehensive tool for crawling websites, single pages, and sitemaps to yield
  markdown content. Use when the agent needs to read or extract knowledge from
  online documentation, parse entire websites recursively, extract markdown from a
  single URL, chunk markdown, or bulk-process URLs from a sitemap XML.
license: MIT
tags: [web, crawler, documentation, docs, scrapper, scrape, extract, markdown, sitemap]
metadata:
  author: Genius
  version: '0.18.0'
---
# Web Crawler Skill

This skill provides a robust CLI script (`scripts/crawl.py`) that utilizes `crawl4ai` to scrape websites, chunk markdown, process sitemaps, and recursively extract pages.

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

### Knowledge Graph Ingestion (Native)

If the user requests that the crawled content be ingested into the Knowledge Graph (or if you are fetching documentation meant for persistent agent memory), you MUST ingest the resulting output directory natively into `graph-os`.

To do this, after the crawler finishes saving the markdown files to the `--output-dir`:
1. Use the `mcp_graph-os_graph_ingest` tool with `action='ingest'` and `target_path` set to the absolute path of your `--output-dir`.
2. Alternatively, if the user explicitly asks to "trigger knowledge-graph-ingest", you can invoke the `knowledge-graph-ingest` skill which will handle the orchestration.

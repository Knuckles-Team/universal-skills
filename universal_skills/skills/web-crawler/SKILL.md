---
name: web-crawler
description: Comprehensive tool for crawling websites, single pages, and sitemaps to yield markdown content. Use when the agent needs to read or extract knowledge from online documentation, parse entire websites recursively, extract markdown from a single URL, chunk markdown, or bulk-process URLs from a sitemap XML.
categories: [Data & Documents, Core]
tags: [web, crawler, documentation, docs, scrapper, scrape, extract, markdown, sitemap]
---

# Web Crawler Skill

This skill provides a robust CLI script (`scripts/crawl.py`) that utilizes `crawl4ai` to scrape websites, chunk markdown, process sitemaps, and recursively extract pages.

## Usage

Use the provided `scripts/crawl.py` to extract text from websites. Always consider if you need to output to a file or stdout. For single pages, stdout is fine. For sitemaps and recursive crawls, always specify `--output-dir`.

```bash
python scripts/crawl.py <url> --strategy <strategy> [options]
```

### Strategies

1. **`single`**: Crawls a single page.
   * `python scripts/crawl.py https://example.com/page --strategy single`
2. **`chunked`**: Crawls a single page and splits the markdown by H1/H2 headers (# or ##).
   * `python scripts/crawl.py https://example.com/page --strategy chunked`
3. **`sitemap-sequential`**: Fetches all URLs in a `sitemap.xml` and crawls them one by one, reusing the browser session. Best for small numbers of URLs when you need reliable parsing without taxing the target server.
   * `python scripts/crawl.py https://example.com/sitemap.xml --strategy sitemap-sequential --output-dir ./docs`
4. **`sitemap-parallel`**: Fetches all URLs in a `sitemap.xml` and crawls them concurrently (memory adaptive dispatch). Best for large documentation sites.
   * `python scripts/crawl.py https://example.com/sitemap.xml --strategy sitemap-parallel --max-concurrent 10 --output-dir ./docs`
5. **`recursive`**: Crawls a site starting from a single URL and recursively follows internal links up to a depth limit, deduplicating URLs.
   * `python scripts/crawl.py https://example.com/ --strategy recursive --max-depth 2 --output-dir ./crawled_content`

### Options

* `--max-depth`: Max recursion depth for `recursive` (default: 3).
* `--max-concurrent`: Number of parallel browser sessions for `sitemap-parallel` and `recursive` (default: 10).
* `--output-dir`: Important! Directory to save markdown. If omitted, prints everything to stdout (not recommended for large crawls!). Saves as `.md` files prefixed by URL scheme or depth.

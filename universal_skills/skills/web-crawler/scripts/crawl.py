#!/usr/bin/env python3
try:
    import psutil
    import requests
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CrawlerRunConfig,
        CacheMode,
        MemoryAdaptiveDispatcher,
    )
except ImportError:
    print("Error: Missing required dependencies for the 'web-crawler' skill.")
    print("Please install them by running: pip install 'universal-skills[web-crawler]'")
    import sys

    sys.exit(1)

import asyncio
import argparse
import os
import re
import logging
import sys
from typing import List
from xml.etree import ElementTree
from urllib.parse import urlparse, urldefrag

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import psutil
    import requests
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CrawlerRunConfig,
        CacheMode,
        MemoryAdaptiveDispatcher,
    )
except ImportError:
    logger.error("Missing required dependencies for the 'web-crawler' skill.")
    logger.error(
        "Please install them by running: pip install 'universal-skills[web-crawler]'"
    )
    sys.exit(1)


def log_memory(process, peak_memory, prefix: str = ""):
    current_mem = process.memory_info().rss  # in bytes
    if current_mem > peak_memory[0]:
        peak_memory[0] = current_mem
    logger.info(
        f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory[0] // (1024 * 1024)} MB"
    )


def extract_markdown(result):
    if hasattr(result, "markdown_v2") and result.markdown_v2:
        return getattr(
            result.markdown_v2,
            "raw_markdown",
            getattr(result.markdown_v2, "fit_markdown", str(result.markdown_v2)),
        )
    if hasattr(result, "markdown") and hasattr(result.markdown, "raw_markdown"):
        return result.markdown.raw_markdown
    if hasattr(result, "markdown") and isinstance(result.markdown, str):
        return result.markdown
    return str(getattr(result, "markdown", ""))


def save_markdown(content: str, url: str, output_dir: str, prefix: str = ""):
    if not output_dir:
        print(f"\n--- Output for {url} ---\n{content}\n")
        return

    os.makedirs(output_dir, exist_ok=True)
    parsed = urlparse(url)

    # Clean slug generation
    path_slug = parsed.path.strip("/").replace("/", "_") or "index"
    if not path_slug.endswith(".md"):
        path_slug += ".md"

    filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "", path_slug)
    if prefix:
        filename = f"{prefix}_{filename}"

    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to save {url} to {filepath}: {e}")
        return False


def cleanup_filenames(output_dir: str):
    """
    Scans the output_dir for .md files and removes common redundant prefixes.
    A prefix is considered redundant if it's present in a majority of files
    (> 50% and at least 5 files).
    """
    if not output_dir or not os.path.isdir(output_dir):
        return

    files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
    if len(files) < 5:
        return

    # Count prefix occurrences
    prefix_counts = {}
    for f in files:
        parts = f.split("_")
        if len(parts) > 1:
            # We check prefixes of increasing length (token by token)
            current_prefix = ""
            for i in range(len(parts) - 1):
                if current_prefix:
                    current_prefix += "_"
                current_prefix += parts[i]
                prefix_counts[current_prefix] = prefix_counts.get(current_prefix, 0) + 1

    # Find the longest prefix that appears in > 50% of files
    best_prefix = None
    threshold = len(files) / 2
    for prefix, count in sorted(
        prefix_counts.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if count > threshold:
            best_prefix = prefix
            break

    if not best_prefix:
        return

    logger.info(f"Cleaning up redundant prefix: '{best_prefix}_'")
    prefix_with_underscore = f"{best_prefix}_"

    for f in files:
        if f.startswith(prefix_with_underscore):
            new_name = f[len(prefix_with_underscore) :]
            if not new_name or new_name == ".md":
                new_name = "index.md"

            old_path = os.path.join(output_dir, f)
            new_path = os.path.join(output_dir, new_name)

            # Avoid collisions
            if os.path.exists(new_path) and old_path != new_path:
                logger.warning(f"Skipping rename of {f} to {new_name}: target exists.")
                continue

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                logger.error(f"Failed to rename {f} to {new_name}: {e}")


async def crawl_single(crawler, url: str, crawl_config, output_dir: str):
    logger.info(f"Crawling single page: {url}")
    result = await crawler.arun(url=url, config=crawl_config)
    if result.success:
        md = extract_markdown(result)
        save_markdown(md, url, output_dir)
    else:
        logger.error(f"Failed to crawl {url}: {result.error_message}")


async def crawl_chunked(crawler, url: str, crawl_config, output_dir: str):
    logger.info(f"Crawling and chunking: {url}")
    result = await crawler.arun(url=url, config=crawl_config)
    if not result.success:
        logger.error(f"Failed to crawl {url}: {result.error_message}")
        return

    markdown = extract_markdown(result)
    header_pattern = re.compile(r"^(# .+|## .+)$", re.MULTILINE)
    headers = [m.start() for m in header_pattern.finditer(markdown)] + [len(markdown)]
    chunks = []
    for i in range(len(headers) - 1):
        chunk = markdown[headers[i] : headers[i + 1]].strip()
        if chunk:
            chunks.append(chunk)

    logger.info(f"Split into {len(chunks)} chunks.")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        parsed = urlparse(url)
        safe_name = parsed.path.strip("/").replace("/", "_") or "index"
        for idx, chunk in enumerate(chunks):
            filepath = os.path.join(output_dir, f"{safe_name}_chunk_{idx+1}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chunk)
            logger.info(f"Saved chunk {idx+1} to {filepath}")
    else:
        for idx, chunk in enumerate(chunks):
            print(f"\n--- Chunk {idx+1} ---\n{chunk}\n")


def fetch_sitemap_urls(sitemap_url: str) -> List[str]:
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall(".//ns:loc", namespace)]
        return urls
    except Exception as e:
        logger.error(f"Error fetching sitemap: {e}")
        return []


async def crawl_sitemap_sequential(
    crawler, sitemap_url: str, crawl_config, output_dir: str
):
    urls = fetch_sitemap_urls(sitemap_url)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return
    logger.info(f"Found {len(urls)} URLs to crawl sequentially.")
    session_id = "sitemap_session"
    for url in urls:
        result = await crawler.arun(url=url, config=crawl_config, session_id=session_id)
        if result.success:
            logger.info(f"Successfully crawled: {url}")
            md = extract_markdown(result)
            save_markdown(md, url, output_dir)
        else:
            logger.error(f"Failed: {url} - Error: {result.error_message}")


async def crawl_sitemap_parallel(
    crawler,
    sitemap_url: str,
    crawl_config,
    dispatcher,
    output_dir: str,
    process,
    peak_memory,
):
    urls = fetch_sitemap_urls(sitemap_url)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return
    logger.info(f"Found {len(urls)} URLs to crawl in parallel.")

    log_memory(process, peak_memory, "Before crawl:")
    results = await crawler.arun_many(
        urls=urls, config=crawl_config, dispatcher=dispatcher
    )

    success_count = 0
    fail_count = 0
    for result in results:
        if result.success:
            success_count += 1
            md = extract_markdown(result)
            save_markdown(md, result.url, output_dir)
        else:
            logger.error(f"Error crawling {result.url}: {result.error_message}")
            fail_count += 1

    logger.info("\nSummary:")
    logger.info(f"  - Successfully crawled: {success_count}")
    logger.info(f"  - Failed: {fail_count}")
    log_memory(process, peak_memory, "After crawl:")


def normalize_url(url):
    return urldefrag(url)[0]


async def crawl_recursive_high_speed(
    crawler,
    start_urls: List[str],
    max_depth: int,
    crawl_config,
    dispatcher,
    output_dir: str,
):
    visited = set()
    current_urls = {normalize_url(u) for u in start_urls}
    allowed_domains = {urlparse(u).netloc for u in start_urls}
    total_saved = 0

    for depth in range(max_depth):
        logger.info(f"Crawling Depth {depth+1}, URLs: {len(current_urls)}")

        urls_to_crawl = []
        for u in current_urls:
            if u not in visited:
                # Start or same domain check
                if depth == 0 or urlparse(u).netloc in allowed_domains:
                    urls_to_crawl.append(u)

        if not urls_to_crawl:
            break

        results = await crawler.arun_many(
            urls=urls_to_crawl, config=crawl_config, dispatcher=dispatcher
        )

        next_level_urls = set()
        for result in results:
            norm_url = normalize_url(result.url)
            visited.add(norm_url)

            if result.success:
                md = extract_markdown(result)
                if save_markdown(md, norm_url, output_dir):
                    total_saved += 1

                # Collect internal links for next depth
                links = result.links.get("internal", [])
                for link in links:
                    next_url = normalize_url(link["href"])
                    if next_url not in visited:
                        next_level_urls.add(next_url)
            else:
                logger.error(f"Failed to crawl {norm_url}: {result.error_message}")

        current_urls = next_level_urls

    logger.info(f"Crawl complete. Total files saved: {total_saved}")


async def main():
    parser = argparse.ArgumentParser(
        description="High-speed Web Crawler Skill using Crawl4AI"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="One or more starting URLs or Sitemap XML URLs",
    )
    parser.add_argument(
        "--strategy",
        choices=[
            "single",
            "chunked",
            "sitemap-sequential",
            "sitemap-parallel",
            "recursive",
        ],
        default="recursive",
        help="Crawling strategy to use. Defaults to 'recursive'.",
    )
    parser.add_argument(
        "--max-depth",
        "--max_depth",
        type=int,
        default=3,
        help="Max recursion depth for 'recursive' strategy.",
    )
    parser.add_argument(
        "--max-concurrent",
        "--max_concurrent",
        type=int,
        default=10,
        help="Max concurrent sessions for parallel strategies.",
    )
    parser.add_argument(
        "--output-dir",
        "--output_dir",
        type=str,
        help="Directory to save markdown files. If not provided, prints to stdout.",
    )

    args = parser.parse_args()

    process = psutil.Process(os.getpid())
    peak_memory = [0]

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False,
        # Wait for content to load for SPAs
        js_code="await new Promise(r => setTimeout(r, 10000));",
        wait_for="body",
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=args.max_concurrent,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        if args.strategy == "single":
            for url in args.urls:
                await crawl_single(crawler, url, crawl_config, args.output_dir)
        elif args.strategy == "chunked":
            for url in args.urls:
                await crawl_chunked(crawler, url, crawl_config, args.output_dir)
        elif args.strategy == "sitemap-sequential":
            for url in args.urls:
                await crawl_sitemap_sequential(
                    crawler, url, crawl_config, args.output_dir
                )
        elif args.strategy == "sitemap-parallel":
            for url in args.urls:
                await crawl_sitemap_parallel(
                    crawler,
                    url,
                    crawl_config,
                    dispatcher,
                    args.output_dir,
                    process,
                    peak_memory,
                )
        elif args.strategy == "recursive":
            await crawl_recursive_high_speed(
                crawler,
                args.urls,
                args.max_depth,
                crawl_config,
                dispatcher,
                args.output_dir,
            )

        if args.output_dir:
            cleanup_filenames(args.output_dir)


if __name__ == "__main__":
    asyncio.run(main())

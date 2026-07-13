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
        DefaultMarkdownGenerator,
        PruningContentFilter,
    )
except ImportError:
    print("Error: Missing required dependencies for the 'web-crawler' skill.")
    print("Please install them by running: pip install 'universal-skills[web-crawler]'")
    import sys

    sys.exit(1)


def to_boolean(string=None):
    if isinstance(string, bool):
        return string
    if not string:
        return False
    normalized = str(string).strip().lower()
    return normalized in {"t", "true", "y", "yes", "1"}


import os
import asyncio
import argparse
import hashlib
import re
import logging
import sys
from typing import List
from xml.etree import ElementTree
from urllib.parse import urlparse, urldefrag, urljoin

# Cross-platform-safe filename generation. Prefer the shared util; fall back to a
# compact local copy when this script runs outside the installed package.
try:
    from universal_skills.skill_utilities import portable_name
except Exception:  # pragma: no cover - standalone execution
    _ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    _RESERVED = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    def portable_name(name: str, max_len: int = 80) -> str:
        if not name:
            return "_"
        cleaned = (
            _ILLEGAL.sub("-", name).rstrip(". ").lstrip(" ").replace("~", "-")
        ) or "_"
        stem, dot, ext = cleaned.rpartition(".")
        base, suffix = (stem, dot + ext) if dot and stem else (cleaned, "")
        if base.upper() in _RESERVED:
            base = f"{base}_"
        full = f"{base}{suffix}"
        if len(full) > max_len:
            digest = hashlib.sha1(name.encode("utf-8"), usedforsecurity=False).hexdigest()[:8]
            keep = max(1, max_len - len(suffix) - 9)
            full = f"{base[:keep]}-{digest}{suffix}"
        return full or "_"


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
        DefaultMarkdownGenerator,
        PruningContentFilter,
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


def _prefer_fit(markdown_obj) -> str:
    """Prefer crawl4ai's readability-filtered ``fit_markdown`` over ``raw_markdown``.

    ``fit_markdown`` (populated by the ``PruningContentFilter`` wired into
    ``CrawlerRunConfig`` below) is crawl4ai's boilerplate-stripped rendering —
    nav/sidebar/cookie-banner/footer chrome scored out. ``raw_markdown`` is the
    unfiltered HTML→markdown conversion and still carries that chrome. Fall back
    to ``raw_markdown`` only when no filtered rendering was produced (e.g. the
    content filter judged nothing prunable, or an older crawl4ai without the
    filter wired).
    """
    fit = getattr(markdown_obj, "fit_markdown", "") or ""
    if fit.strip():
        return fit
    return getattr(markdown_obj, "raw_markdown", "") or str(markdown_obj)


def extract_markdown(result):
    md = ""
    if hasattr(result, "markdown_v2") and result.markdown_v2:
        md = _prefer_fit(result.markdown_v2)
    elif hasattr(result, "markdown") and hasattr(result.markdown, "raw_markdown"):
        md = _prefer_fit(result.markdown)
    elif hasattr(result, "markdown") and isinstance(result.markdown, str):
        md = result.markdown
    else:
        md = str(getattr(result, "markdown", ""))

    return clean_markdown(md.strip())


_MULTI_BLANK_RE = re.compile(r"\n{3,}")
_TRAILING_WS_RE = re.compile(r"[ \t]+\n")
_FINGERPRINT_WS_RE = re.compile(r"\s+")


def clean_markdown(md: str) -> str:
    """Collapse incidental whitespace crawl4ai/the content filter leaves behind.

    Strips trailing whitespace on each line and collapses 3+ consecutive blank
    lines to a single blank line, without touching the actual content — this
    runs on every page regardless of dedup so saved/ingested markdown is tidy.
    """
    if not md:
        return md
    md = _TRAILING_WS_RE.sub("\n", md)
    md = _MULTI_BLANK_RE.sub("\n\n", md)
    return md.strip()


def content_fingerprint(md: str) -> str:
    """A normalized content hash for near-duplicate detection across a crawl.

    Lowercases and collapses all whitespace before hashing so two pages that
    differ only by incidental formatting (or a trailing timestamp/whitespace)
    still fingerprint identically.
    """
    normalized = _FINGERPRINT_WS_RE.sub(" ", md.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8", "surrogatepass")).hexdigest()


def is_duplicate_content(md: str, seen_fingerprints: set, *, min_chars: int = 40) -> bool:
    """True (and records the fingerprint) if ``md`` duplicates an already-seen page.

    Short/empty pages (below ``min_chars``) are never deduped by content — they're
    dropped for emptiness elsewhere, not flagged as duplicates of each other.
    """
    if len(md) < min_chars:
        return False
    fp = content_fingerprint(md)
    if fp in seen_fingerprints:
        return True
    seen_fingerprints.add(fp)
    return False


def save_markdown(content: str, url: str, output_dir: str, prefix: str = ""):
    if not output_dir:
        print(f"\n--- Output for {url} ---\n{content}\n")
        return

    os.makedirs(output_dir, exist_ok=True)
    parsed = urlparse(url)

    # Clean slug generation (cross-platform safe: length-bounded, no illegal chars).
    path_slug = parsed.path.strip("/").replace("/", "_") or "index"
    if not path_slug.endswith(".md"):
        path_slug += ".md"

    if prefix:
        path_slug = f"{prefix}_{path_slug}"
    filename = portable_name(path_slug)

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


class KGIngestor:
    """Natively ingests each crawled page into graph-os / epistemic-graph over MCP.

    CONCEPT:AU-KG.ingest.chunk-overlap-stage — graph-os is reached exactly the way
    the platform does: over its **MCP streamable-http surface** (``<endpoint>/mcp``,
    a JSON-RPC ``tools/call`` after an ``initialize`` handshake). graph-os is a
    dynamic multiplexer, so the tool is mounted on the session with ``load_tools``
    first. No extra dependency: stdlib ``urllib`` only (the crawler already ships
    ``requests``, but the MCP handshake is kept dependency-light). Two native modes:

    * ``content`` (DEFAULT) — call the ``document_process`` tool with the crawler's
      OWN cleaned ``fit_markdown`` (``document=<md>``, ``source=<url>``). graph-os
      chunks + embeds + (contextual-)enriches OUR refined markdown into a
      ``:Document`` + ``:Chunk`` objects with a content hash. This GUARANTEES the
      clean/refined content is what lands in the KG regardless of the graph-os
      pod's own fetch backend — the crux of "ingest a clean and refined set of
      markdown scraped documents". The Document title is the page's first ``#``
      heading; ``source`` carries the page URL for provenance.
    * ``url`` — call ``graph_ingest`` with ``action='ingest_url'``, ``target_path=<url>``.
      graph-os RE-FETCHES via its own unified resolver (ArchiveBox→crawl4ai→requests)
      into a Document+Concept(+Chunk) with ``source_url``/``ast_hash`` provenance.
      Best when you want graph-os's ArchiveBox snapshot / server-side fetch + its
      concept extraction, and the gateway pod has a strong fetch backend.

    Sticky-disables itself after the first unreachable/failed handshake so a downed
    gateway degrades once (loud) → file-only output, rather than retrying every
    page. Best-effort throughout: a submission failure never aborts the crawl.
    """

    def __init__(
        self,
        endpoint: str,
        token: str = "",
        timeout: float = 60.0,
        ssl_verify: bool = True,
        mode: str = "content",
    ):
        base = endpoint.rstrip("/")
        # Accept either a bare gateway URL or one already ending in /mcp.
        self.mcp_url = base if base.endswith("/mcp") else base + "/mcp"
        self.token = token
        self.timeout = timeout
        self.ssl_verify = ssl_verify
        self.mode = mode if mode in ("content", "url") else "content"
        self.submitted: list[str] = []
        self.errors: list[str] = []
        self.reachable = True
        self._session_id: str | None = None
        self._rid = 0

    # -- MCP streamable-http plumbing (stdlib only) ------------------------

    def _rpc(self, method: str, params: dict, notify: bool = False):
        """One JSON-RPC call over MCP streamable-http; returns parsed result dict."""
        import ssl as _ssl
        import urllib.request

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        body: dict = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            self._rid += 1
            body["id"] = self._rid
        req = urllib.request.Request(
            self.mcp_url,
            data=json.dumps(body).encode(),
            headers=headers,
            method="POST",
        )
        ctx = None
        if self.mcp_url.startswith("https") and not self.ssl_verify:
            ctx = _ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
        resp = urllib.request.urlopen(req, timeout=self.timeout, context=ctx)  # noqa: S310
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self._session_id = sid
        raw = resp.read().decode()
        if notify:
            return None
        # streamable-http replies as SSE ("data: {json}") or plain JSON.
        data = None
        for line in raw.splitlines():
            if line.startswith("data:"):
                try:
                    data = json.loads(line[5:].strip())
                except ValueError:
                    pass
        if data is None and raw.strip():
            data = json.loads(raw)
        return data

    def _ensure_session(self) -> None:
        """Lazy MCP handshake + mount the tool we need (idempotent)."""
        if self._session_id:
            return
        self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "web-crawler-skill", "version": "1.3"},
            },
        )
        self._rpc("notifications/initialized", {}, notify=True)
        tool = "document_process" if self.mode == "content" else "graph_ingest"
        self._rpc("tools/call", {"name": "load_tools", "arguments": {"tools": [tool]}})

    @staticmethod
    def _tool_error(result: dict) -> str | None:
        """Return an error string if the tools/call result is an error, else None."""
        if not isinstance(result, dict):
            return f"unexpected result: {str(result)[:120]}"
        if "error" in result:
            return str(result["error"])[:200]
        inner = result.get("result", {})
        if isinstance(inner, dict) and inner.get("isError"):
            texts = [c.get("text", "") for c in inner.get("content", []) if isinstance(c, dict)]
            return ("; ".join(t for t in texts if t))[:200] or "isError"
        return None

    def submit(self, url: str, markdown: str = "") -> None:
        """Ingest one crawled page into the KG over MCP (best-effort, never raises)."""
        if not self.reachable:
            return
        # 'content' mode needs the cleaned markdown; without it (e.g. an HTTP
        # fallback path that only has the URL) transparently use 'url' mode.
        use_content = self.mode == "content" and bool(markdown.strip())
        try:
            self._ensure_session()
            if use_content:
                name = "document_process"
                arguments = {"document": markdown, "source": url, "contextual": True}
            else:
                name = "graph_ingest"
                arguments = {"action": "ingest_url", "target_path": url}
                # graph_ingest may not be mounted if mode started as 'content'.
                self._rpc(
                    "tools/call",
                    {"name": "load_tools", "arguments": {"tools": [name]}},
                )
            result = self._rpc("tools/call", {"name": name, "arguments": arguments})
            err = self._tool_error(result)
            if err:
                raise RuntimeError(err)
            self.submitted.append(url)
            logger.info(
                f"KG ingest ({'content' if use_content else 'url'}) ok for {url}"
            )
        except Exception as e:  # noqa: BLE001 - best-effort, must not abort the crawl
            self.reachable = False
            self.errors.append(f"{url}: {e}")
            logger.warning(
                f"KG ingestion unreachable at {self.mcp_url} ({e}); falling back "
                "to file-only output for the remainder of this crawl."
            )

    def summary(self) -> str:
        if not self.submitted and not self.errors:
            return "KG ingestion: no pages submitted."
        parts = [
            f"KG ingestion ({self.mode}): {len(self.submitted)} page(s) "
            f"ingested via {self.mcp_url}"
        ]
        if self.errors:
            parts.append(f"{len(self.errors)} submission(s) failed (first: {self.errors[0]})")
        return "; ".join(parts)


async def crawl_single(crawler, url: str, crawl_config, output_dir: str, kg_ingestor=None):
    logger.info(f"Crawling single page: {url}")
    result = await crawler.arun(url=url, config=crawl_config)
    if result.success:
        md = extract_markdown(result)
        save_markdown(md, url, output_dir)
        if kg_ingestor and md.strip():
            kg_ingestor.submit(url, md)
    else:
        logger.error(f"Failed to crawl {url}: {result.error_message}")


async def crawl_chunked(crawler, url: str, crawl_config, output_dir: str, kg_ingestor=None):
    logger.info(f"Crawling and chunking: {url}")
    result = await crawler.arun(url=url, config=crawl_config)
    if not result.success:
        logger.error(f"Failed to crawl {url}: {result.error_message}")
        return

    markdown = extract_markdown(result)
    if kg_ingestor and markdown.strip():
        # The header-chunking below is a local file-splitting convenience; graph-os
        # ingests the whole cleaned page as one Document (it does its own chunking).
        kg_ingestor.submit(url, markdown)
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
            filepath = os.path.join(
                output_dir, portable_name(f"{safe_name}_chunk_{idx + 1}.md")
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chunk)
            logger.info(f"Saved chunk {idx + 1} to {filepath}")
    else:
        for idx, chunk in enumerate(chunks):
            print(f"\n--- Chunk {idx + 1} ---\n{chunk}\n")


def fetch_sitemap_urls(
    sitemap_url: str, ssl_verify: bool = True, _depth: int = 0
) -> List[str]:
    if _depth > 3:  # Guard against infinite recursion
        return []
    try:
        response = requests.get(sitemap_url, verify=ssl_verify, timeout=15)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Sitemap index: recursively fetch child sitemaps
        child_sitemaps = root.findall(".//ns:sitemap/ns:loc", namespace)
        if child_sitemaps:
            all_urls = []
            for child_loc in child_sitemaps:
                child_urls = fetch_sitemap_urls(
                    child_loc.text, ssl_verify=ssl_verify, _depth=_depth + 1
                )
                all_urls.extend(child_urls)
            return all_urls

        # Regular sitemap: return all <url><loc> entries (skip .xml files)
        urls = [
            loc.text
            for loc in root.findall(".//ns:loc", namespace)
            if loc.text and not loc.text.rstrip("/").endswith(".xml")
        ]
        return urls
    except Exception as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
        return []


def discover_sitemap(start_url: str, ssl_verify: bool = True) -> str | None:
    """Check robots.txt for Sitemap: line, fallback to /sitemap.xml"""
    parsed = urlparse(start_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_url}/robots.txt"
    try:
        r = requests.get(robots_url, verify=ssl_verify, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    # Fallback
    candidate = f"{base_url}/sitemap.xml"
    try:
        r = requests.head(candidate, verify=ssl_verify, timeout=5)
        if r.status_code in (200, 301, 302):
            return candidate
    except Exception:
        pass
    return None


async def crawl_sitemap_sequential(
    crawler,
    sitemap_url: str,
    crawl_config,
    output_dir: str,
    ssl_verify: bool = True,
    allowed_prefixes: List[str] = None,
    kg_ingestor=None,
    seen_fingerprints: set = None,
):
    urls = fetch_sitemap_urls(sitemap_url, ssl_verify=ssl_verify)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return

    if allowed_prefixes:
        logger.info(f"Filtering sitemap URLs by prefixes: {allowed_prefixes}")
        original_count = len(urls)
        urls = [
            u
            for u in urls
            if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
        ]
        logger.info(f"Filtered {original_count} URLs down to {len(urls)}")

    if not urls:
        logger.warning("No URLs remaining after filtering.")
        return

    logger.info(f"Found {len(urls)} URLs to crawl sequentially.")
    session_id = "sitemap_session"
    seen = seen_fingerprints if seen_fingerprints is not None else set()
    for url in urls:
        result = await crawler.arun(url=url, config=crawl_config, session_id=session_id)
        if result.success:
            md = extract_markdown(result)
            if not md.strip():
                logger.warning(f"Empty content, skipping: {url}")
                continue
            if is_duplicate_content(md, seen):
                logger.info(f"Skipping near-duplicate page: {url}")
                continue
            logger.info(f"Successfully crawled: {url}")
            save_markdown(md, url, output_dir)
            if kg_ingestor:
                kg_ingestor.submit(url, md)
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
    ssl_verify: bool = True,
    allowed_prefixes: List[str] = None,
    kg_ingestor=None,
    seen_fingerprints: set = None,
):
    urls = fetch_sitemap_urls(sitemap_url, ssl_verify=ssl_verify)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return

    if allowed_prefixes:
        logger.info(f"Filtering sitemap URLs by prefixes: {allowed_prefixes}")
        original_count = len(urls)
        urls = [
            u
            for u in urls
            if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
        ]
        logger.info(f"Filtered {original_count} URLs down to {len(urls)}")

    if not urls:
        logger.warning("No URLs remaining after filtering.")
        return

    logger.info(f"Found {len(urls)} URLs to crawl in parallel.")

    log_memory(process, peak_memory, "Before crawl:")
    results = await crawler.arun_many(
        urls=urls, config=crawl_config, dispatcher=dispatcher
    )

    seen = seen_fingerprints if seen_fingerprints is not None else set()
    success_count = 0
    fail_count = 0
    duplicate_count = 0
    for result in results:
        if result.success:
            md = extract_markdown(result)
            if not md.strip():
                fail_count += 1
                continue
            if is_duplicate_content(md, seen):
                duplicate_count += 1
                logger.info(f"Skipping near-duplicate page: {result.url}")
                continue
            success_count += 1
            save_markdown(md, result.url, output_dir)
            if kg_ingestor:
                kg_ingestor.submit(result.url, md)
        else:
            logger.error(f"Error crawling {result.url}: {result.error_message}")
            fail_count += 1

    logger.info("\nSummary:")
    logger.info(f"  - Successfully crawled: {success_count}")
    logger.info(f"  - Duplicates skipped: {duplicate_count}")
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
    max_pages: int = 1000,
    ignore_prefix_restriction: bool = False,
    ssl_verify: bool = True,
    kg_ingestor=None,
):
    seen_fingerprints: set = set()
    duplicate_count = 0
    visited = set()
    current_urls = {normalize_url(u) for u in start_urls}
    allowed_domains = {urlparse(u).netloc for u in start_urls}

    # Compute the common path prefix across start URLs to stay focused.
    # E.g. for "/docs/r/api-reference/foo.html" the prefix becomes "/docs/".
    # We take the first two path segments (e.g. "/docs/") so sub-pages are included.
    def _path_prefix(url):
        parts = urlparse(url).path.strip("/").split("/")
        # Use first segment only (e.g. "docs") as the scope boundary
        return "/" + parts[0] + "/" if parts and parts[0] else "/"

    allowed_prefixes = {_path_prefix(u) for u in start_urls}
    logger.info(f"Restricting crawl to path prefixes: {allowed_prefixes}")

    total_saved = 0
    max_pages = max_pages
    ignore_prefix = ignore_prefix_restriction

    for depth in range(max_depth):
        if total_saved >= max_pages:
            logger.warning(f"Reached max pages limit ({max_pages}). Stopping.")
            break
        logger.info(f"Crawling Depth {depth + 1}, URLs: {len(current_urls)}")

        urls_to_crawl = []
        for u in current_urls:
            if u not in visited:
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

                # Filter out access-denied pages
                if (
                    md
                    and "Access Denied" not in md
                    and "permission to access" not in md
                ):
                    if is_duplicate_content(md, seen_fingerprints):
                        duplicate_count += 1
                        logger.info(f"Skipping near-duplicate page: {norm_url}")
                    elif save_markdown(md, norm_url, output_dir):
                        total_saved += 1
                        if kg_ingestor:
                            kg_ingestor.submit(norm_url, md)
                else:
                    logger.warning(
                        f"Skipping {norm_url}: Access Denied or content blocked"
                    )

                # Collect internal links for next depth, resolving relative hrefs
                links = result.links.get("internal", [])
                logger.info(f"DEBUG: Found {len(links)} internal links for {norm_url}")
                for link in links:
                    href = link.get("href", "")
                    if not href:
                        continue
                    # Resolve relative URLs against the current page URL
                    if not href.startswith(("http://", "https://")):
                        href = urljoin(norm_url, href)
                    next_url = normalize_url(href)
                    if next_url not in visited:
                        next_level_urls.add(next_url)
            else:
                logger.error(f"Failed to crawl {norm_url}: {result.error_message}")

        # Filter internal links to allowed prefixes (fixes the dead code)
        if not ignore_prefix and allowed_prefixes and next_level_urls:
            next_level_urls = {
                u
                for u in next_level_urls
                if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
            }

        logger.info(
            f"DEBUG: Extracted {len(next_level_urls)} unique new links for next depth"
        )
        current_urls = next_level_urls

    logger.info(
        f"Crawl complete. Total files saved: {total_saved} "
        f"(duplicates skipped: {duplicate_count})"
    )


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
        "--no-sitemap", action="store_true", help="Disable sitemap auto-discovery"
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
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL verification (Use with caution)",
    )
    parser.add_argument(
        "--disable-magic-js",
        action="store_true",
        help="Disable the complex MAGIC_JS payload",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1000,
        help="Limit the total number of pages crawled in recursive mode.",
    )
    parser.add_argument(
        "--ignore-prefix-restriction",
        action="store_true",
        help="Do not restrict recursive crawling to the starting path prefix.",
    )
    parser.add_argument(
        "--wait-for",
        type=str,
        help="Custom CSS selector or JS expression to wait for.",
    )
    parser.add_argument(
        "--no-kg-ingest",
        "--no_kg_ingest",
        action="store_true",
        help="Disable native Knowledge Graph ingestion (default: ON). Every "
        "successfully crawled, deduped page is ingested into graph-os / "
        "epistemic-graph (Document+Chunk with provenance) as it is crawled; "
        "pass this to get file-only output. Degrades automatically (with a "
        "warning) if graph-os is unreachable.",
    )
    parser.add_argument(
        "--kg-mode",
        "--kg_mode",
        choices=["content", "url"],
        default="content",
        help="How to ingest into the KG. 'content' (default) pushes THIS "
        "crawler's cleaned fit_markdown via document_process → a clean "
        "Document+Chunk regardless of graph-os's own fetch backend. 'url' "
        "submits just the URL via graph_ingest ingest_url → graph-os re-fetches "
        "(ArchiveBox/crawl4ai/requests) and also extracts Concepts.",
    )
    parser.add_argument(
        "--kg-endpoint",
        "--kg_endpoint",
        type=str,
        default="",
        help="graph-os gateway base URL for KG ingestion (else $GRAPH_OS_URL, "
        "default http://graph-os.arpa).",
    )

    args = parser.parse_args()

    # Precedence: Env Var SSL_VERIFY > CLI --insecure > Default (True)
    ssl_verify_env = os.getenv("SSL_VERIFY")
    if ssl_verify_env is not None:
        ssl_verify = to_boolean(ssl_verify_env)
    elif args.insecure:
        ssl_verify = False
    else:
        ssl_verify = True

    # Auto-discovery of sitemap
    original_seed_urls = list(args.urls)
    discovered_sitemap = None
    if not args.no_sitemap:
        for url in args.urls:
            sitemap = discover_sitemap(url, ssl_verify=ssl_verify)
            if sitemap:
                logger.info(f"Auto-discovered sitemap: {sitemap}")
                if args.strategy == "recursive":
                    logger.info(
                        "Switching to sitemap-parallel strategy for complete coverage."
                    )
                    args.strategy = "sitemap-parallel"
                discovered_sitemap = sitemap
                args.urls = [sitemap]  # Update args.urls with the discovered sitemap
                break  # Stop after finding the first sitemap

    # Determine allowed prefixes for filtering (only if we auto-discovered a sitemap)
    allowed_prefixes = None
    if discovered_sitemap and not args.ignore_prefix_restriction:

        def _path_prefix(url):
            parsed = urlparse(url)
            path = parsed.path
            if not path or path == "/":
                return "/"
            parts = path.strip("/").split("/")
            # If it looks like a deep path, use a stricter prefix
            if len(parts) > 1:
                return "/" + "/".join(parts[:2]) + "/"
            return "/" + (parts[0] if parts else "") + "/"

        allowed_prefixes = [_path_prefix(u) for u in original_seed_urls]

    process = psutil.Process(os.getpid())
    peak_memory = [0]

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    MAGIC_JS = """
    (async () => {
        // 1. Initial scrolls to trigger lazy loading
        window.scrollTo(0, 0);
        await new Promise(r => setTimeout(r, 500));
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 1000));

        // 2. Dispatch ESCAPE key to clear popups
        for (let i = 0; i < 3; i++) {
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true }));
            await new Promise(r => setTimeout(r, 200));
        }

        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 500));
        window.scrollTo(0, 0);
        await new Promise(r => setTimeout(r, 500));

        // 3. Scroll through the page and remove popups/fixed elements
        let scrollHeight = document.body.scrollHeight || 1080;
        let innerHeight = window.innerHeight || 1080;
        let maxScroll = 15000;
        if (scrollHeight > maxScroll) scrollHeight = maxScroll;

        for (let offset = 0; offset <= scrollHeight; offset += innerHeight) {
            window.scrollTo(0, offset);
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true }));
            await new Promise(r => setTimeout(r, 200));

            // Handle locked scrollbars
            try {
                for (let e of document.getElementsByClassName("Scroll--locked")) {
                    e.style.overflow = "hidden";
                    e.style.position = "relative";
                }
                let htmlElem = document.querySelector('html');
                if (htmlElem) {
                    htmlElem.style.overflow = 'hidden';
                    htmlElem.style.position = 'relative';
                }
            } catch (e) {}

            // Remove dynamically floating fixed/sticky popups/cookie banners, but guard against deleting SPA root containers
            // Temporarily disabled floating popup removal to test if it's the culprit destroying ServiceNow's root DOM
            /*
            try {
                let elements = document.querySelectorAll('div, dialog');
                for (let i = 0; i < elements.length; i++) {
                    let style = window.getComputedStyle(elements[i]);
                    if (style.position === 'fixed' || style.position === 'sticky' || style.position === '-webkit-sticky') {
                        let zIdx = parseInt(style.zIndex, 10);
                        if (isNaN(zIdx) || zIdx < 10) continue;
                        if (elements[i].innerText && elements[i].innerText.length > 2000) continue;
                        if (elements[i].clientWidth > window.innerWidth * 0.9 && elements[i].clientHeight > window.innerHeight * 0.9) continue;
                        elements[i].parentNode.removeChild(elements[i]);
                    }
                }
            } catch (e) {}
            */
        }

        // 4. Purge all headers, footers, sidebars from the DOM natively, fulfilling the user's request
        try {
            let noiseElements = document.querySelectorAll('header, footer, aside, [role="banner"], [role="contentinfo"]');
            noiseElements.forEach(el => el.remove());
        } catch(e) {}

        // 5. Reset scroll to top and explicitly enable scroll
        window.scrollTo(0, 0);
        try {
            let body = document.querySelector('body');
            if (body) body.setAttribute('style', 'overflow: scroll; overflow-x: scroll;');
            let html = document.querySelector('html');
            if (html) html.setAttribute('style', 'overflow: scroll; overflow-x: scroll;');
        } catch(e) {}

        // Final wait to ensure content stabilizes
        await new Promise(r => setTimeout(r, 2000));
    })();
    """

    # Improved wait_for logic with fallback
    default_wait_for = """js:() => {
        // Primary: common content containers
        let els = document.querySelectorAll('main, article, #content, .content, [role="main"], .md-content, .doc-content, .markdown');
        for (let e of els) {
            if (e.innerText && e.innerText.length > 30) return true;
        }
        // Fallback: any body text at all
        return document.body && document.body.innerText.length > 100;
    }"""

    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # Clean & refined markdown (CONCEPT:AU-KG.ingest.web-fetch-front-door): score out nav/sidebar/
        # cookie-banner/footer chrome via crawl4ai's pruning content filter so
        # ``result.markdown.fit_markdown`` (preferred by extract_markdown()) is
        # substantive content, not raw HTML→markdown of the whole page.
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),
        # Enable basic anti-bot evasion techniques (simulates human, sets headers, hides webdriver flags)
        magic=True,
        wait_until="networkidle",
        # Wait for the main body/article to explicitly populate with text, bypassing cookie banner race conditions
        wait_for=args.wait_for or default_wait_for,
        # Execute JS to clear popups, remove fixed navigation/modals, and explicitly blast headers/footers
        js_code=None if args.disable_magic_js else MAGIC_JS,
        # Process iframes natively, which many enterprise techdocs use (e.g. ServiceNow)
        process_iframes=True,
        page_timeout=90000,
        wait_for_timeout=30000,
        delay_before_return_html=3.0,
        # Exclude common noise elements (Notice: 'nav' is intentionally omitted to protect the API Index which resides in a <nav>)
        # excluded_tags=["footer", "header"],
        exclude_external_links=True,
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=args.max_concurrent,
    )

    # Native Knowledge Graph ingestion (CONCEPT:AU-KG.ingest.chunk-overlap-stage) — default ON. Every
    # crawled, cleaned, deduped page is ingested into graph-os / epistemic-graph
    # as it's found (default 'content' mode → push cleaned markdown via
    # document_process; 'url' mode → graph_ingest ingest_url). Disabled with
    # --no-kg-ingest, and this internal crawl subprocess (invoked by
    # agent-utilities as ITS OWN crawl4ai fetch backend, e.g.
    # web_fetch._fetch_via_crawl4ai / skill_graph_pipeline) always passes
    # --no-kg-ingest to avoid recursing back into ingestion or double-ingesting
    # a corpus that pipeline already ingests itself.
    kg_ingestor = None
    if not args.no_kg_ingest:
        kg_endpoint = (
            args.kg_endpoint
            or os.getenv("GRAPH_OS_URL", "").strip()
            or "http://graph-os.arpa"
        )
        kg_ingestor = KGIngestor(
            kg_endpoint,
            token=os.getenv("GRAPH_OS_TOKEN", "").strip(),
            ssl_verify=ssl_verify,
            mode=args.kg_mode,
        )
    seen_fingerprints: set = set()

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            if args.strategy == "single":
                for url in args.urls:
                    await crawl_single(
                        crawler, url, crawl_config, args.output_dir, kg_ingestor=kg_ingestor
                    )
            elif args.strategy == "chunked":
                for url in args.urls:
                    await crawl_chunked(
                        crawler, url, crawl_config, args.output_dir, kg_ingestor=kg_ingestor
                    )
            elif args.strategy == "sitemap-sequential":
                for url in args.urls:
                    await crawl_sitemap_sequential(
                        crawler,
                        url,
                        crawl_config,
                        args.output_dir,
                        ssl_verify=ssl_verify,
                        allowed_prefixes=allowed_prefixes
                        if discovered_sitemap
                        else None,
                        kg_ingestor=kg_ingestor,
                        seen_fingerprints=seen_fingerprints,
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
                        ssl_verify=ssl_verify,
                        allowed_prefixes=allowed_prefixes
                        if discovered_sitemap
                        else None,
                        kg_ingestor=kg_ingestor,
                        seen_fingerprints=seen_fingerprints,
                    )
            elif args.strategy == "recursive":
                await crawl_recursive_high_speed(
                    crawler,
                    args.urls,
                    args.max_depth,
                    crawl_config,
                    dispatcher,
                    args.output_dir,
                    max_pages=args.max_pages,
                    ignore_prefix_restriction=args.ignore_prefix_restriction,
                    ssl_verify=ssl_verify,
                    kg_ingestor=kg_ingestor,
                )
    except Exception as e:
        logger.warning(f"crawl4ai/Playwright execution failed: {e}")
        logger.warning("Attempting graceful fallback using standard HTTP requests...")
        import requests

        # Fallback is currently best-effort for single/chunked URLs.
        # Complex recursion/sitemap logic requires the full headless browser engine.
        if args.strategy in ("single", "chunked"):
            for url in args.urls:
                try:
                    logger.info(f"Fallback fetching: {url}")
                    resp = requests.get(url, verify=ssl_verify, timeout=15)
                    resp.raise_for_status()

                    content = resp.text
                    # Try to strip HTML if BeautifulSoup is available
                    try:
                        from bs4 import BeautifulSoup

                        soup = BeautifulSoup(content, "html.parser")
                        content = soup.get_text(separator="\n", strip=True)
                    except ImportError:
                        pass

                    save_markdown(content, url, args.output_dir)
                    if kg_ingestor and content.strip():
                        # Our local fetch degraded to plain HTTP; still hand the
                        # URL to graph-os's own resolver chain (which may reach
                        # ArchiveBox/crawl4ai server-side) rather than pushing
                        # this low-quality extraction into the KG ourselves.
                        kg_ingestor.submit(url)
                except Exception as ex:
                    logger.error(f"Fallback fetch failed for {url}: {ex}")
        else:
            logger.error(
                f"Fallback extraction is not supported for strategy '{args.strategy}'. Please run 'playwright install' to fix the browser dependencies."
            )

    if args.output_dir:
        cleanup_filenames(args.output_dir)

    if kg_ingestor:
        logger.info(kg_ingestor.summary())


if __name__ == "__main__":
    asyncio.run(main())

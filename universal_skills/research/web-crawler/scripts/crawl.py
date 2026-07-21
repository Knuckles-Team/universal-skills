#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse
from xml.etree import ElementTree

try:
    from security_runtime import (
        MAX_LINKS_PER_PAGE,
        MAX_SEED_URLS,
        MAX_SITEMAP_BYTES,
        MAX_SITEMAP_DEPTH,
        MAX_SITEMAP_URLS,
        CrawlerSecurityError,
        CrawlerSecurityPolicy,
        OutputBudget,
        SafeMCPClient,
    )
except ImportError:
    print("Web crawler security runtime is unavailable.", file=sys.stderr)
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:  # Browser dependencies are optional and gated by AgentConfig.
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CacheMode,
        CrawlerRunConfig,
        DefaultMarkdownGenerator,
        MemoryAdaptiveDispatcher,
        PruningContentFilter,
    )
except ImportError:
    AsyncWebCrawler = None
    BrowserConfig = None
    CacheMode = None
    CrawlerRunConfig = None
    DefaultMarkdownGenerator = None
    MemoryAdaptiveDispatcher = None
    PruningContentFilter = None

try:
    import psutil
except ImportError:
    psutil = None


def log_memory(process, peak_memory, prefix: str = ""):
    if process is None:
        return
    try:
        current_mem = process.memory_info().rss  # in bytes
    except Exception:
        return
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


def extract_markdown(result, policy: CrawlerSecurityPolicy) -> str:
    md = ""
    if hasattr(result, "markdown_v2") and result.markdown_v2:
        md = _prefer_fit(result.markdown_v2)
    elif hasattr(result, "markdown") and hasattr(result.markdown, "raw_markdown"):
        md = _prefer_fit(result.markdown)
    elif hasattr(result, "markdown") and isinstance(result.markdown, str):
        md = result.markdown
    else:
        md = str(getattr(result, "markdown", ""))

    clean, redactions = policy.sanitize_content(clean_markdown(md.strip()))
    if redactions:
        logger.info("Applied %d privacy redaction(s) to crawled content", redactions)
    return clean


_MULTI_BLANK_RE = re.compile(r"\n{3,}")
_TRAILING_WS_RE = re.compile(r"[ \t]+\n")
_FINGERPRINT_WS_RE = re.compile(r"\s+")
_MAX_XML_ELEMENTS = 30_000
_MAX_XML_DEPTH = 64
_MAX_CHUNKS_PER_PAGE = 512


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


def is_duplicate_content(
    md: str, seen_fingerprints: set, *, min_chars: int = 40
) -> bool:
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


def parse_bounded_sitemap_xml(body: bytes) -> Any:
    """Parse sitemap XML with explicit entity, element, and depth ceilings."""

    upper_body = body.upper()
    if b"<!DOCTYPE" in upper_body or b"<!ENTITY" in upper_body:
        raise CrawlerSecurityError("crawler_sitemap_unsafe_xml")
    parser = ElementTree.XMLPullParser(events=("start", "end"))
    depth = 0
    elements = 0
    root = None

    def consume_events() -> None:
        nonlocal depth, elements, root
        for event, element in parser.read_events():
            if event == "start":
                depth += 1
                elements += 1
                if root is None:
                    root = element
                if depth > _MAX_XML_DEPTH or elements > _MAX_XML_ELEMENTS:
                    raise CrawlerSecurityError("crawler_sitemap_structure_too_large")
            else:
                depth -= 1
                if depth < 0:
                    raise CrawlerSecurityError("crawler_sitemap_invalid")

    for offset in range(0, len(body), 64 * 1024):
        parser.feed(body[offset : offset + 64 * 1024])
        consume_events()
    parser.close()
    consume_events()
    if root is None or depth != 0:
        raise CrawlerSecurityError("crawler_sitemap_invalid")
    return root


def save_markdown(
    content: str,
    url: str,
    output_dir: Path | None,
    policy: CrawlerSecurityPolicy,
    prefix: str = "",
) -> bool:
    if not output_dir:
        try:
            clean = policy.reserve_output(content)
            print(f"\n--- Crawled output ---\n{clean}\n")
            return True
        except Exception:
            logger.error("Crawler output budget was exceeded")
            return False
    try:
        return policy.write_markdown(output_dir, content, url, suffix=prefix)
    except Exception:
        logger.error("Failed to save crawled content")
        return False


class KGIngestor:
    """Best-effort, bounded MCP ingestion of privacy-sanitized page content."""

    def __init__(
        self,
        endpoint: str,
        policy: CrawlerSecurityPolicy,
        token: str = "",
        timeout: float = 60.0,
    ):
        self.policy = policy
        self.client = SafeMCPClient(
            endpoint,
            policy=policy,
            token=token,
            timeout=timeout,
        )
        self.submitted = 0
        self.errors = 0
        self.reachable = True
        self._rid = 0
        self._submission_budget = OutputBudget()

    def _rpc(self, method: str, params: dict, notify: bool = False):
        body: dict = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            self._rid += 1
            body["id"] = self._rid
        return self.client.post(body, notify=notify)

    def _ensure_session(self) -> None:
        """Lazy MCP handshake + mount the tool we need (idempotent)."""
        if self.client.session_id:
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
        self._rpc(
            "tools/call",
            {"name": "load_tools", "arguments": {"tools": ["document_process"]}},
        )

    @staticmethod
    def _tool_error(result: dict) -> str | None:
        """Return a stable error code without retaining upstream output."""
        if not isinstance(result, dict):
            return "kg_result_invalid"
        if "error" in result:
            return "kg_rpc_error"
        inner = result.get("result", {})
        if isinstance(inner, dict) and inner.get("isError"):
            return "kg_tool_error"
        return None

    def submit(self, url: str, markdown: str = "") -> None:
        """Ingest one crawled page into the KG over MCP (best-effort, never raises)."""
        if not self.reachable:
            return
        if not markdown.strip():
            return
        try:
            self._ensure_session()
            clean, _ = self.policy.sanitize_content(markdown)
            self._submission_budget.consume(len(clean.encode("utf-8")))
            arguments = {
                "document": clean,
                "source": self.policy.source_reference(url),
                "contextual": True,
            }
            result = self._rpc(
                "tools/call",
                {"name": "document_process", "arguments": arguments},
            )
            err = self._tool_error(result)
            if err:
                raise RuntimeError(err)
            self.submitted += 1
            logger.info("Knowledge Graph ingestion succeeded")
        except Exception:  # noqa: BLE001 - best-effort must not abort the crawl
            self.reachable = False
            self.errors += 1
            logger.warning(
                "Knowledge Graph ingestion is unavailable; continuing with local output"
            )

    def summary(self) -> str:
        if self.submitted == 0 and self.errors == 0:
            return "KG ingestion: no pages submitted."
        parts = [f"KG ingestion: {self.submitted} page(s) ingested"]
        if self.errors:
            parts.append(f"{self.errors} submission(s) failed")
        return "; ".join(parts)


class _HTMLTextExtractor(HTMLParser):
    """Small dependency-free HTML-to-text/link extractor for the safe HTTP path."""

    _BLOCK_TAGS = frozenset(
        {
            "article",
            "br",
            "div",
            "footer",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "header",
            "li",
            "main",
            "p",
            "section",
            "tr",
        }
    )
    _IGNORED_TAGS = frozenset({"script", "style", "noscript", "template"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.casefold()
        if normalized in self._IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if normalized in self._BLOCK_TAGS:
            self.parts.append("\n")
        if normalized == "a" and len(self.links) < MAX_LINKS_PER_PAGE:
            href = next(
                (value for key, value in attrs if key.casefold() == "href"), None
            )
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if normalized in self._IGNORED_TAGS:
            self._ignored_depth = max(0, self._ignored_depth - 1)
            return
        if not self._ignored_depth and normalized in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data:
            self.parts.append(data)


@dataclass
class _CrawlResult:
    success: bool
    url: str
    markdown: str = ""
    links: dict[str, list[dict[str, str]]] = field(
        default_factory=lambda: {"internal": []}
    )


class SafeHttpCrawler:
    """Default crawler: bounded HTTP fetches with no browser execution surface."""

    def __init__(self, policy: CrawlerSecurityPolicy, max_concurrent: int) -> None:
        self.policy = policy
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._batch_size = max_concurrent * 2

    async def __aenter__(self) -> "SafeHttpCrawler":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        return None

    async def arun(
        self, *, url: str, config: Any = None, **_kwargs: Any
    ) -> _CrawlResult:
        del config
        try:
            normalized = self.policy.validate_url(url)
            async with self._semaphore:
                html = await asyncio.to_thread(self.policy.fetch_text, normalized)
            parser = _HTMLTextExtractor()
            parser.feed(html)
            markdown = clean_markdown("".join(parser.parts))
            origin = self.policy.origin(normalized)
            links: list[dict[str, str]] = []
            for raw_href in parser.links[:MAX_LINKS_PER_PAGE]:
                try:
                    resolved = self.policy.require_scoped_url(
                        urljoin(normalized, raw_href),
                        allowed_origins={origin},
                        resolve_dns=False,
                    )
                except CrawlerSecurityError:
                    continue
                links.append({"href": resolved})
            return _CrawlResult(
                success=True,
                url=normalized,
                markdown=markdown,
                links={"internal": links},
            )
        except Exception:
            return _CrawlResult(success=False, url="")

    async def arun_many(
        self,
        *,
        urls: list[str],
        config: Any = None,
        dispatcher: Any = None,
    ) -> list[_CrawlResult]:
        del dispatcher
        results: list[_CrawlResult] = []
        for offset in range(0, len(urls), self._batch_size):
            results.extend(
                await asyncio.gather(
                    *(
                        self.arun(url=url, config=config)
                        for url in urls[offset : offset + self._batch_size]
                    ),
                )
            )
        return results


class GuardedBrowserCrawler:
    """Browser adapter with safe top-level preflight and post-navigation checks."""

    def __init__(
        self,
        crawler: Any,
        policy: CrawlerSecurityPolicy,
        max_concurrent: int,
    ) -> None:
        self.crawler = crawler
        self.policy = policy
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._batch_size = max_concurrent * 2

    async def arun(self, *, url: str, config: Any = None, **kwargs: Any) -> Any:
        try:
            normalized = self.policy.validate_url(url)
            # Central HTTP preflight validates DNS and every redirect before the
            # more privileged browser is allowed to navigate.
            await asyncio.to_thread(self.policy.fetch_bytes, normalized)
            async with self._semaphore:
                result = await self.crawler.arun(
                    url=normalized,
                    config=config,
                    **kwargs,
                )
            if not getattr(result, "success", False):
                return result
            final_url = self.policy.require_scoped_url(
                getattr(result, "url", normalized),
                allowed_origins={self.policy.origin(normalized)},
            )
            result.url = final_url
            return result
        except Exception:
            return _CrawlResult(success=False, url="")

    async def arun_many(
        self,
        *,
        urls: list[str],
        config: Any = None,
        dispatcher: Any = None,
    ) -> list[Any]:
        del dispatcher
        results: list[Any] = []
        for offset in range(0, len(urls), self._batch_size):
            results.extend(
                await asyncio.gather(
                    *(
                        self.arun(url=url, config=config)
                        for url in urls[offset : offset + self._batch_size]
                    ),
                )
            )
        return results


async def crawl_single(
    crawler,
    url: str,
    crawl_config,
    output_dir: Path | None,
    policy: CrawlerSecurityPolicy,
    kg_ingestor=None,
):
    logger.info("Crawling one configured page")
    result = await crawler.arun(url=url, config=crawl_config)
    if result.success:
        md = extract_markdown(result, policy)
        save_markdown(md, result.url, output_dir, policy)
        if kg_ingestor and md.strip():
            kg_ingestor.submit(result.url, md)
    else:
        logger.error("Crawl failed; upstream details omitted")


async def crawl_chunked(
    crawler,
    url: str,
    crawl_config,
    output_dir: Path | None,
    policy: CrawlerSecurityPolicy,
    kg_ingestor=None,
):
    logger.info("Crawling and chunking one configured page")
    result = await crawler.arun(url=url, config=crawl_config)
    if not result.success:
        logger.error("Crawl failed; upstream details omitted")
        return

    markdown = extract_markdown(result, policy)
    if kg_ingestor and markdown.strip():
        # The header-chunking below is a local file-splitting convenience; graph-os
        # ingests the whole cleaned page as one Document (it does its own chunking).
        kg_ingestor.submit(result.url, markdown)
    header_pattern = re.compile(r"^(# .+|## .+)$", re.MULTILINE)
    headers: list[int] = []
    for match in header_pattern.finditer(markdown):
        headers.append(match.start())
        if len(headers) >= _MAX_CHUNKS_PER_PAGE - 1:
            break
    if not headers or headers[0] != 0:
        headers.insert(0, 0)
    headers.append(len(markdown))
    chunks = []
    for i in range(len(headers) - 1):
        chunk = markdown[headers[i] : headers[i + 1]].strip()
        if chunk:
            chunks.append(chunk)

    logger.info("Split content into %d chunk(s)", len(chunks))
    for idx, chunk in enumerate(chunks):
        save_markdown(
            chunk,
            result.url,
            output_dir,
            policy,
            prefix=f"chunk-{idx + 1}",
        )
    if output_dir:
        logger.info("Saved %d chunk(s)", len(chunks))


def fetch_sitemap_urls(
    sitemap_url: str,
    policy: CrawlerSecurityPolicy,
    *,
    max_urls: int = MAX_SITEMAP_URLS,
    _depth: int = 0,
    _visited: set[str] | None = None,
    _allowed_origins: set[str] | None = None,
) -> list[str]:
    """Fetch bounded sitemap XML while retaining the seed origin boundary."""

    max_urls = max(1, min(int(max_urls), MAX_SITEMAP_URLS))
    if _depth > MAX_SITEMAP_DEPTH:
        return []
    visited = _visited if _visited is not None else set()
    try:
        normalized = policy.validate_url(sitemap_url)
        if normalized in visited or len(visited) >= MAX_SITEMAP_URLS:
            return []
        visited.add(normalized)
        origins = _allowed_origins or {policy.origin(normalized)}
        normalized = policy.require_scoped_url(
            normalized,
            allowed_origins=origins,
        )
        body = policy.fetch_bytes(normalized, max_bytes=MAX_SITEMAP_BYTES)
        root = parse_bounded_sitemap_xml(body)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Sitemap index: recursively fetch child sitemaps
        child_sitemaps = root.findall(".//ns:sitemap/ns:loc", namespace)
        if child_sitemaps:
            all_urls: list[str] = []
            for child_loc in child_sitemaps[:max_urls]:
                if not child_loc.text:
                    continue
                try:
                    child_url = policy.require_scoped_url(
                        child_loc.text,
                        allowed_origins=origins,
                        resolve_dns=False,
                    )
                except CrawlerSecurityError:
                    continue
                child_urls = fetch_sitemap_urls(
                    child_url,
                    policy,
                    max_urls=max_urls - len(all_urls),
                    _depth=_depth + 1,
                    _visited=visited,
                    _allowed_origins=origins,
                )
                all_urls.extend(child_urls)
                if len(all_urls) >= max_urls:
                    break
            return list(dict.fromkeys(all_urls))[:max_urls]

        urls: list[str] = []
        for loc in root.findall(".//ns:url/ns:loc", namespace)[:max_urls]:
            if not loc.text:
                continue
            try:
                candidate = policy.require_scoped_url(
                    loc.text,
                    allowed_origins=origins,
                    resolve_dns=False,
                )
            except CrawlerSecurityError:
                continue
            urls.append(candidate)
        return urls
    except Exception:
        logger.error("Sitemap fetch failed")
        return []


def discover_sitemap(
    start_url: str,
    policy: CrawlerSecurityPolicy,
) -> str | None:
    """Check bounded robots.txt and sitemap.xml inside the seed trust scope."""

    try:
        normalized = policy.validate_url(start_url)
    except Exception:
        return None
    parsed = urlparse(normalized)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    origins = {policy.origin(normalized)}
    robots_url = f"{base_url}/robots.txt"
    try:
        robots = policy.fetch_text(robots_url, max_bytes=512 * 1024)
        for line in robots.splitlines()[:10_000]:
            if line.casefold().startswith("sitemap:"):
                return policy.require_scoped_url(
                    line.split(":", 1)[1].strip(),
                    allowed_origins=origins,
                )
    except Exception:
        pass
    candidate = f"{base_url}/sitemap.xml"
    try:
        policy.fetch_bytes(candidate, max_bytes=MAX_SITEMAP_BYTES)
        return policy.require_scoped_url(candidate, allowed_origins=origins)
    except Exception:
        pass
    return None


async def crawl_sitemap_sequential(
    crawler,
    sitemap_url: str,
    crawl_config,
    output_dir: Path | None,
    policy: CrawlerSecurityPolicy,
    max_pages: int,
    allowed_prefixes: list[str] | None = None,
    kg_ingestor=None,
    seen_fingerprints: set | None = None,
):
    urls = fetch_sitemap_urls(sitemap_url, policy, max_urls=max_pages)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return 0

    if allowed_prefixes:
        logger.info("Filtering sitemap URLs by configured path scope")
        original_count = len(urls)
        urls = [
            u
            for u in urls
            if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
        ]
        logger.info(f"Filtered {original_count} URLs down to {len(urls)}")

    if not urls:
        logger.warning("No URLs remaining after filtering.")
        return 0

    logger.info(f"Found {len(urls)} URLs to crawl sequentially.")
    session_id = "sitemap_session"
    seen = seen_fingerprints if seen_fingerprints is not None else set()
    for url in urls:
        result = await crawler.arun(url=url, config=crawl_config, session_id=session_id)
        if result.success:
            md = extract_markdown(result, policy)
            if not md.strip():
                logger.warning("Empty content; skipping configured URL")
                continue
            if is_duplicate_content(md, seen):
                logger.info("Skipping near-duplicate page")
                continue
            logger.info("Page crawl succeeded")
            save_markdown(md, result.url, output_dir, policy)
            if kg_ingestor:
                kg_ingestor.submit(result.url, md)
        else:
            logger.error("Crawl failed; upstream details omitted")
    return len(urls)


async def crawl_sitemap_parallel(
    crawler,
    sitemap_url: str,
    crawl_config,
    dispatcher,
    output_dir: Path | None,
    process,
    peak_memory,
    policy: CrawlerSecurityPolicy,
    max_pages: int,
    allowed_prefixes: list[str] | None = None,
    kg_ingestor=None,
    seen_fingerprints: set | None = None,
):
    urls = fetch_sitemap_urls(sitemap_url, policy, max_urls=max_pages)
    if not urls:
        logger.warning("No URLs found in sitemap.")
        return 0

    if allowed_prefixes:
        logger.info("Filtering sitemap URLs by configured path scope")
        original_count = len(urls)
        urls = [
            u
            for u in urls
            if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
        ]
        logger.info(f"Filtered {original_count} URLs down to {len(urls)}")

    if not urls:
        logger.warning("No URLs remaining after filtering.")
        return 0

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
            md = extract_markdown(result, policy)
            if not md.strip():
                fail_count += 1
                continue
            if is_duplicate_content(md, seen):
                duplicate_count += 1
                logger.info("Skipping near-duplicate page")
                continue
            success_count += 1
            save_markdown(md, result.url, output_dir, policy)
            if kg_ingestor:
                kg_ingestor.submit(result.url, md)
        else:
            logger.error("Crawl failed; upstream details omitted")
            fail_count += 1

    logger.info("\nSummary:")
    logger.info(f"  - Successfully crawled: {success_count}")
    logger.info(f"  - Duplicates skipped: {duplicate_count}")
    logger.info(f"  - Failed: {fail_count}")
    log_memory(process, peak_memory, "After crawl:")
    return len(urls)


def normalize_url(url):
    return urldefrag(url)[0]


async def crawl_recursive_high_speed(
    crawler,
    start_urls: list[str],
    max_depth: int,
    crawl_config,
    dispatcher,
    output_dir: Path | None,
    policy: CrawlerSecurityPolicy,
    max_pages: int = 1000,
    ignore_prefix_restriction: bool = False,
    kg_ingestor=None,
):
    seen_fingerprints: set = set()
    duplicate_count = 0
    visited = set()
    current_urls = {policy.validate_url(normalize_url(u)) for u in start_urls}
    allowed_origins = {policy.origin(u) for u in current_urls}

    # Compute the common path prefix across start URLs to stay focused.
    # E.g. for "/docs/r/api-reference/foo.html" the prefix becomes "/docs/".
    # We take the first two path segments (e.g. "/docs/") so sub-pages are included.
    def _path_prefix(url):
        parts = urlparse(url).path.strip("/").split("/")
        # Use first segment only (e.g. "docs") as the scope boundary
        return "/" + parts[0] + "/" if parts and parts[0] else "/"

    allowed_prefixes = {_path_prefix(u) for u in start_urls}
    logger.info("Restricting recursive crawl to configured origin and path scope")

    total_saved = 0
    ignore_prefix = ignore_prefix_restriction

    for depth in range(max_depth):
        if len(visited) >= max_pages:
            logger.warning("Reached configured page limit; stopping")
            break
        logger.info("Crawling depth %d with %d URL(s)", depth + 1, len(current_urls))

        urls_to_crawl = []
        for u in current_urls:
            if u not in visited:
                if policy.origin(u) in allowed_origins:
                    urls_to_crawl.append(u)

        if not urls_to_crawl:
            break
        urls_to_crawl = urls_to_crawl[: max_pages - len(visited)]
        # Count attempts, not only successful writes, so failures and blocked
        # pages cannot bypass the global crawl budget.
        visited.update(urls_to_crawl)

        results = await crawler.arun_many(
            urls=urls_to_crawl, config=crawl_config, dispatcher=dispatcher
        )

        next_level_urls = set()
        for result in results:
            try:
                norm_url = policy.require_scoped_url(
                    normalize_url(result.url),
                    allowed_origins=allowed_origins,
                )
            except CrawlerSecurityError:
                logger.error("Crawl result violated the configured origin policy")
                continue
            visited.add(norm_url)

            if result.success:
                md = extract_markdown(result, policy)

                # Filter out access-denied pages
                if (
                    md
                    and "Access Denied" not in md
                    and "permission to access" not in md
                ):
                    if is_duplicate_content(md, seen_fingerprints):
                        duplicate_count += 1
                        logger.info("Skipping near-duplicate page")
                    elif save_markdown(md, norm_url, output_dir, policy):
                        total_saved += 1
                        if kg_ingestor:
                            kg_ingestor.submit(norm_url, md)
                else:
                    logger.warning(
                        "Skipping URL because access was denied or content was blocked"
                    )

                # Collect internal links for next depth, resolving relative hrefs
                links = result.links.get("internal", [])[:MAX_LINKS_PER_PAGE]
                logger.info("Found %d bounded internal link(s)", len(links))
                for link in links:
                    href = link.get("href", "")
                    if not href:
                        continue
                    # Resolve relative URLs against the current page URL
                    if not href.startswith(("http://", "https://")):
                        href = urljoin(norm_url, href)
                    try:
                        next_url = policy.require_scoped_url(
                            normalize_url(href),
                            allowed_origins=allowed_origins,
                            resolve_dns=False,
                        )
                    except CrawlerSecurityError:
                        continue
                    if next_url not in visited:
                        next_level_urls.add(next_url)
            else:
                logger.error("Crawl failed; upstream details omitted")

        # Filter internal links to allowed prefixes (fixes the dead code)
        if not ignore_prefix and allowed_prefixes and next_level_urls:
            next_level_urls = {
                u
                for u in next_level_urls
                if any(urlparse(u).path.startswith(p) for p in allowed_prefixes)
            }

        logger.info(
            "Extracted %d bounded unique link(s) for the next depth",
            len(next_level_urls),
        )
        current_urls = set(list(next_level_urls)[:max_pages])

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
        default=4,
        help="Max concurrent sessions for parallel strategies.",
    )
    parser.add_argument(
        "--output-dir",
        "--output_dir",
        type=str,
        help="Workspace-relative or approved XDG/workspace directory for markdown.",
    )
    parser.add_argument(
        "--disable-magic-js",
        action="store_true",
        help="Disable the complex MAGIC_JS payload",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
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
        help="Custom CSS selector to wait for in explicitly enabled browser mode.",
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
        "--kg-endpoint",
        "--kg_endpoint",
        type=str,
        default="",
        help="graph-os gateway base URL for KG ingestion (else $GRAPH_OS_URL).",
    )

    args = parser.parse_args()

    try:
        policy = CrawlerSecurityPolicy.from_agent_config()
        if not 1 <= len(args.urls) <= MAX_SEED_URLS:
            raise CrawlerSecurityError("crawler_seed_count_invalid")
        if not 1 <= args.max_depth <= 8:
            raise CrawlerSecurityError("crawler_depth_invalid")
        if not 1 <= args.max_concurrent <= 16:
            raise CrawlerSecurityError("crawler_concurrency_invalid")
        if not 1 <= args.max_pages <= MAX_SITEMAP_URLS:
            raise CrawlerSecurityError("crawler_page_limit_invalid")
        if args.wait_for:
            selector = str(args.wait_for).strip()
            if (
                not selector
                or len(selector.encode("utf-8")) > 256
                or selector.casefold().startswith("js:")
                or any(ord(character) < 32 for character in selector)
            ):
                raise CrawlerSecurityError("crawler_wait_selector_invalid")
            args.wait_for = "css:" + selector.removeprefix("css:")
        args.urls = [policy.validate_url(url) for url in args.urls][: args.max_pages]
        output_dir = policy.resolve_output_dir(args.output_dir)
    except Exception:
        logger.error("Crawler configuration was rejected by the security policy")
        return

    # Auto-discovery of sitemap
    original_seed_urls = list(args.urls)
    discovered_sitemap = None
    if not args.no_sitemap:
        for url in args.urls:
            sitemap = discover_sitemap(url, policy)
            if sitemap:
                logger.info("Auto-discovered an approved sitemap")
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

    try:
        process = psutil.Process(os.getpid()) if psutil is not None else None
    except Exception:
        process = None
    peak_memory = [0]

    browser_config = None
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

    crawl_config = None
    dispatcher = None
    if policy.allow_browser_fetch:
        browser_dependencies = (
            AsyncWebCrawler,
            BrowserConfig,
            CacheMode,
            CrawlerRunConfig,
            DefaultMarkdownGenerator,
            MemoryAdaptiveDispatcher,
            PruningContentFilter,
        )
        if any(dependency is None for dependency in browser_dependencies):
            logger.error("Browser fetching is enabled but its runtime is unavailable")
            return
        try:
            browser_arguments = policy.browser_arguments(args.urls)
            browser_config = BrowserConfig(
                headless=True,
                verbose=False,
                # Chromium sandboxing remains enabled.
                extra_args=browser_arguments,
            )
            crawl_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter()
                ),
                magic=True,
                wait_until="networkidle",
                wait_for=args.wait_for or default_wait_for,
                js_code=None if args.disable_magic_js else MAGIC_JS,
                # Iframes can silently expand the browser's egress boundary.
                process_iframes=False,
                page_timeout=45_000,
                wait_for_timeout=15_000,
                delay_before_return_html=1.0,
                exclude_external_links=True,
            )
            dispatcher = MemoryAdaptiveDispatcher(
                memory_threshold_percent=70.0,
                check_interval=1.0,
                max_session_permit=args.max_concurrent,
            )
        except Exception:
            logger.error("Browser transport configuration is unsupported")
            return

    # Native Knowledge Graph ingestion (CONCEPT:AU-KG.ingest.chunk-overlap-stage) — default ON. Every
    # crawled, cleaned, deduped page is ingested into graph-os / epistemic-graph
    # as it's found (privacy-sanitized content via document_process). Disabled with
    # --no-kg-ingest, and this internal crawl subprocess (invoked by
    # agent-utilities as ITS OWN crawl4ai fetch backend, e.g.
    # web_fetch._fetch_via_crawl4ai / skill_graph_pipeline) always passes
    # --no-kg-ingest to avoid recursing back into ingestion or double-ingesting
    # a corpus that pipeline already ingests itself.
    kg_ingestor = None
    if not args.no_kg_ingest:
        kg_endpoint = args.kg_endpoint or os.getenv("GRAPH_OS_URL", "").strip()
        if kg_endpoint:
            try:
                kg_ingestor = KGIngestor(
                    kg_endpoint,
                    policy=policy,
                    token=os.getenv("GRAPH_OS_TOKEN", "").strip(),
                )
            except Exception:
                logger.warning("Knowledge Graph endpoint configuration was rejected")
        else:
            print(
                "Knowledge Graph ingestion skipped: no graph endpoint configured.",
                file=sys.stderr,
            )
    seen_fingerprints: set = set()

    async def run_selected_strategy(crawler: Any) -> None:
        scoped_prefixes = allowed_prefixes if discovered_sitemap else None
        if args.strategy == "single":
            for url in args.urls:
                await crawl_single(
                    crawler,
                    url,
                    crawl_config,
                    output_dir,
                    policy,
                    kg_ingestor=kg_ingestor,
                )
        elif args.strategy == "chunked":
            for url in args.urls:
                await crawl_chunked(
                    crawler,
                    url,
                    crawl_config,
                    output_dir,
                    policy,
                    kg_ingestor=kg_ingestor,
                )
        elif args.strategy == "sitemap-sequential":
            remaining = args.max_pages
            for url in args.urls:
                if remaining <= 0:
                    break
                attempted = await crawl_sitemap_sequential(
                    crawler,
                    url,
                    crawl_config,
                    output_dir,
                    policy,
                    remaining,
                    allowed_prefixes=scoped_prefixes,
                    kg_ingestor=kg_ingestor,
                    seen_fingerprints=seen_fingerprints,
                )
                remaining -= attempted
        elif args.strategy == "sitemap-parallel":
            remaining = args.max_pages
            for url in args.urls:
                if remaining <= 0:
                    break
                attempted = await crawl_sitemap_parallel(
                    crawler,
                    url,
                    crawl_config,
                    dispatcher,
                    output_dir,
                    process,
                    peak_memory,
                    policy,
                    remaining,
                    allowed_prefixes=scoped_prefixes,
                    kg_ingestor=kg_ingestor,
                    seen_fingerprints=seen_fingerprints,
                )
                remaining -= attempted
        elif args.strategy == "recursive":
            await crawl_recursive_high_speed(
                crawler,
                args.urls,
                args.max_depth,
                crawl_config,
                dispatcher,
                output_dir,
                policy,
                max_pages=args.max_pages,
                ignore_prefix_restriction=args.ignore_prefix_restriction,
                kg_ingestor=kg_ingestor,
            )

    try:
        if policy.allow_browser_fetch:
            async with AsyncWebCrawler(config=browser_config) as browser:
                crawler = GuardedBrowserCrawler(
                    browser,
                    policy,
                    args.max_concurrent,
                )
                await run_selected_strategy(crawler)
        else:
            async with SafeHttpCrawler(policy, args.max_concurrent) as crawler:
                await run_selected_strategy(crawler)
    except Exception:
        logger.error("Crawler execution failed")

    if kg_ingestor:
        logger.info(kg_ingestor.summary())


if __name__ == "__main__":
    asyncio.run(main())

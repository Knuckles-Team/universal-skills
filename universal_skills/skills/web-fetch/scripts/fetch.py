#!/usr/bin/env python3
"""Compatibility entry point for the consolidated web-crawler skill.

This module intentionally contains no transport or browser implementation. It
reuses web-crawler's AgentConfig-backed SSRF, DNS, redirect, TLS, privacy, and
resource boundaries so the legacy single-page command cannot drift into a
second fetch stack.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def _crawler_runtime():
    """Load the sibling implementation only when an actual fetch is requested."""

    scripts = Path(__file__).resolve().parents[2] / "web-crawler" / "scripts"
    if not scripts.is_dir() or scripts.is_symlink():
        raise RuntimeError("crawler_runtime_unavailable")
    sys.path.insert(0, str(scripts))
    try:
        from crawl import SafeHttpCrawler, extract_markdown
        from security_runtime import CrawlerSecurityPolicy
    except ImportError:
        raise RuntimeError("crawler_runtime_unavailable") from None
    return SafeHttpCrawler, extract_markdown, CrawlerSecurityPolicy


async def fetch_page(url: str) -> tuple[str, str]:
    """Fetch one page through web-crawler's shared hardened HTTP path."""

    SafeHttpCrawler, extract_markdown, CrawlerSecurityPolicy = _crawler_runtime()
    policy = CrawlerSecurityPolicy.from_agent_config()
    normalized = policy.validate_url(url)
    async with SafeHttpCrawler(policy, max_concurrent=1) as crawler:
        result = await crawler.arun(url=normalized, config=None)
    if not getattr(result, "success", False):
        raise RuntimeError("fetch_failed")
    content = policy.reserve_output(extract_markdown(result, policy))
    return policy.source_reference(normalized), content


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch one page through the consolidated web-crawler runtime."
    )
    parser.add_argument("--url", required=True, help="Public HTTP(S) URL to fetch.")
    parser.add_argument("--json", action="store_true", help="Emit bounded JSON.")
    parser.add_argument(
        "--prompt",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if args.prompt:
        print(
            "Embedded LLM extraction was retired; analyze the sanitized fetch "
            "result through the governed agent runtime.",
            file=sys.stderr,
        )
        return 2
    try:
        source_ref, result = await fetch_page(args.url)
    except Exception:
        print("Configured fetch failed.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"source_ref": source_ref, "result": result}))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

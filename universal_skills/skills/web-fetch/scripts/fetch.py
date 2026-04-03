#!/usr/bin/env python3
import asyncio
import argparse
import sys
import os
import json
from typing import Optional

try:
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CrawlerRunConfig,
        CacheMode,
    )

    # Lazy load pydantic_ai to avoid dependency issues if only fetching
except ImportError:
    print("Error: Missing required dependencies for the 'web-fetch' skill.")
    print("Please install them by running: pip install 'universal-skills[web-fetch]'")
    sys.exit(1)


async def fetch_page(url: str, prompt: Optional[str] = None):
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,
        wait_until="networkidle",
        process_iframes=True,
        # Exclude common noise elements
        excluded_tags=["header", "footer", "nav", "ads"],
        remove_overlay_elements=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawl_config)

        if not result.success:
            print(f"Error: Failed to fetch {url}: {result.error_message}")
            return None

        # Extract markdown using crawl4ai's high-fidelity extraction
        markdown = ""
        if hasattr(result, "markdown_v2") and result.markdown_v2:
            markdown = getattr(
                result.markdown_v2,
                "raw_markdown",
                getattr(result.markdown_v2, "fit_markdown", str(result.markdown_v2)),
            )
        elif hasattr(result, "markdown"):
            if isinstance(result.markdown, str):
                markdown = result.markdown
            elif hasattr(result.markdown, "raw_markdown"):
                markdown = result.markdown.raw_markdown
            else:
                markdown = str(result.markdown)
        else:
            markdown = str(result)

        markdown = markdown.strip()

        if not prompt:
            return markdown

        # LLM Extraction if prompt is provided
        try:
            from pydantic_ai import Agent
            from pydantic import BaseModel

            class ExtractionResult(BaseModel):
                result: str

            # Use the environment-configured model or fallback to a sensible default
            model = os.getenv("PYDANTIC_AI_MODEL", "anthropic:claude-3-5-sonnet-latest")
            agent = Agent(model, result_type=ExtractionResult)

            user_prompt = (
                f"You are a web content analyst. Extract information from the provided markdown content based on the prompt below.\n"
                f"Prompt: {prompt}\n\n"
                f"Markdown Content:\n{markdown}"
            )

            res = await agent.run(user_prompt)
            return res.data.result
        except ImportError:
            print("Warning: pydantic-ai not installed. Returning raw markdown.")
            return markdown
        except Exception as e:
            print(f"Warning: LLM extraction failed: {e}. Returning raw markdown.")
            return markdown


async def main():
    parser = argparse.ArgumentParser(
        description="Fetch and extract content from a single URL."
    )
    parser.add_argument("--url", required=True, help="The URL to fetch.")
    parser.add_argument(
        "--prompt",
        help="Optional prompt to extract specific information from the content.",
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format.")

    args = parser.parse_args()

    # URL basic validation
    if not args.url.startswith(("http://", "https://")):
        print("Error: Invalid URL scheme. Only http and https are supported.")
        sys.exit(1)

    result = await fetch_page(args.url, args.prompt)

    if result:
        if args.json:
            print(json.dumps({"url": args.url, "result": result}, indent=2))
        else:
            print(result)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

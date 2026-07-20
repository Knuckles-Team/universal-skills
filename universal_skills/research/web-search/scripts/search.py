#!/usr/bin/env python3
import argparse
import json
import os
import sys

from search_bing import search as search_bing
from search_duckduckgo import search as search_duckduckgo
from search_google import search as search_google
from search_searxng import search as search_searxng


def run_search_provider(provider: str, query: str, max_results: int):
    """Dispatch through a fixed in-process provider map; never spawn a command."""

    if provider == "searxng":
        return search_searxng(query, os.environ["SEARXNG_URL"], max_results)
    if provider == "google":
        return search_google(
            query,
            os.environ["GOOGLE_API_KEY"],
            os.environ["GOOGLE_CX"],
            max_results,
        )
    if provider == "bing":
        return search_bing(query, os.environ["BING_API_KEY"], max_results)
    if provider == "duckduckgo":
        return search_duckduckgo(query, max_results)
    raise ValueError("Unsupported search provider")


def main():
    parser = argparse.ArgumentParser(description="Multi-Provider Web Search Dispatcher")
    parser.add_argument("--query", required=True, help="The search query")
    parser.add_argument(
        "--max-results",
        "--max_results",
        type=int,
        default=10,
        help="Maximum number of results to return",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    # Determine which provider to use
    provider = "duckduckgo"  # Default fallback

    if os.environ.get("SEARXNG_URL"):
        provider = "searxng"
    elif os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CX"):
        provider = "google"
    elif os.environ.get("BING_API_KEY"):
        provider = "bing"

    try:
        results = run_search_provider(provider, args.query, args.max_results)
    except Exception:
        results = None

    if results is None:
        # If the preferred one failed, try DuckDuckGo as final fallback
        if provider != "duckduckgo":
            try:
                results = run_search_provider(
                    "duckduckgo", args.query, args.max_results
                )
                provider = "duckduckgo"
            except Exception:
                results = None

    if results is None:
        print("Error: All search providers failed.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"--- Search Results (via {provider}) ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title')}")
            print(f"   URL: {result.get('link')}")
            print(f"   Snippet: {result.get('snippet')}")


if __name__ == "__main__":
    main()

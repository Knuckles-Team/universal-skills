#!/usr/bin/env python3
import argparse
import json
import os
import sys

try:
    from http_runtime import fetch_json, validate_search_request
except ImportError:
    print("Error: Missing required dependencies for the 'web-search' skill.")
    print("Please install them by running: pip install 'universal-skills[web-search]'")
    sys.exit(1)


def search(query: str, base_url: str, max_results: int = 10):
    # Ensure there is no trailing slash
    base_url = base_url.rstrip("/")
    url = f"{base_url}/search"
    results = []

    try:
        query, max_results = validate_search_request(query, max_results)
        params = {"q": query, "format": "json"}
        data = fetch_json(url, params=params)

        items = data.get("results", [])
        for item in items[:max_results]:
            results.append(
                {
                    "title": item.get("title"),
                    "link": item.get("url"),
                    "snippet": item.get("content"),
                }
            )

        return results
    except Exception as exc:
        raise RuntimeError("SearxNG search failed") from exc


def main():
    parser = argparse.ArgumentParser(description="Searxng Web Search")
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

    base_url = os.environ.get("SEARXNG_URL")

    if not base_url:
        print(
            "Error: SEARXNG_BASE_URL environment variable is required.", file=sys.stderr
        )
        sys.exit(1)

    try:
        results = search(args.query, base_url, args.max_results)
    except Exception as exc:
        print(f"Search failed ({type(exc).__name__})", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results found for query: '{args.query}'")
            return

        print(f"--- Searxng Search Results for '{args.query}' ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet']}")


if __name__ == "__main__":
    main()

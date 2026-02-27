#!/usr/bin/env python3
import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Error: Missing required dependencies for the 'web-search' skill.")
    print("Please install them by running: pip install 'universal-skills[web-search]'")
    sys.exit(1)


def search(query: str, searxng_url: str, max_results: int = 10):
    # Ensure there is no trailing slash
    base_url = searxng_url.rstrip("/")
    url = f"{base_url}/search"
    results = []

    try:
        params = {"q": query, "format": "json"}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

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
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error performing Searxng search: {e}", file=sys.stderr)
        sys.exit(1)


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

    searxng_url = os.environ.get("SEARXNG_URL")

    if not searxng_url:
        print("Error: SEARXNG_URL environment variable is required.", file=sys.stderr)
        sys.exit(1)

    results = search(args.query, searxng_url, args.max_results)

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

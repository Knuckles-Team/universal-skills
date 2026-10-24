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


def search(query: str, api_key: str, cx: str, max_results: int = 10):
    url = "https://www.googleapis.com/customsearch/v1"
    results = []

    try:
        query, max_results = validate_search_request(query, max_results)
        # Google Custom Search API returns up to 10 results per page
        # We might need to paginate if max_results > 10, but for simplicity, allow up to 10 for now
        # Or we can do minimal pagination.
        num = min(10, max_results)
        params = {"key": api_key, "cx": cx, "q": query, "num": num}

        data = fetch_json(url, params=params)

        items = data.get("items", [])
        for item in items:
            results.append(
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                }
            )

        return results
    except Exception as exc:
        raise RuntimeError("Google search failed") from exc


def main():
    parser = argparse.ArgumentParser(description="Google Custom Search")
    parser.add_argument("--query", required=True, help="The search query")
    parser.add_argument(
        "--max-results",
        "--max_results",
        type=int,
        default=10,
        help="Maximum number of results to return (up to 10 supported natively without pagination)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_CX")

    if not api_key or not cx:
        print(
            "Error: GOOGLE_API_KEY and GOOGLE_CX environment variables are required.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        results = search(args.query, api_key, cx, args.max_results)
    except Exception as exc:
        print(f"Search failed ({type(exc).__name__})", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results found for query: '{args.query}'")
            return

        print(f"--- Google Search Results for '{args.query}' ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet']}")


if __name__ == "__main__":
    main()

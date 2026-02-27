#!/usr/bin/env python3
import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Error: Missing required dependencies for the 'web-search' skill.")
    print(
        "Please install them by running: pip install 'universal-skills[web-search]'"
    )
    sys.exit(1)


def search(query: str, api_key: str, cx: str, max_results: int = 10):
    url = "https://www.googleapis.com/customsearch/v1"
    results = []

    try:
        # Google Custom Search API returns up to 10 results per page
        # We might need to paginate if max_results > 10, but for simplicity, allow up to 10 for now
        # Or we can do minimal pagination.
        num = min(10, max_results)
        params = {"key": api_key, "cx": cx, "q": query, "num": num}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

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
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - 3", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error performing Google search: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Custom Search")
    parser.add_argument("query", help="The search query")
    parser.add_argument(
        "--max-results",
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

    results = search(args.query, api_key, cx, args.max_results)

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

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


def search(query: str, api_key: str, max_results: int = 10):
    url = "https://api.bing.microsoft.com/v7.0/search"
    results = []

    try:
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": max_results,
            "textDecorations": True,
            "textFormat": "HTML",
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        items = data.get("webPages", {}).get("value", [])
        for item in items:
            results.append(
                {
                    "title": item.get("name"),
                    "link": item.get("url"),
                    "snippet": item.get("snippet"),
                }
            )

        return results
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error performing Bing search: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Bing Web Search")
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

    api_key = os.environ.get("BING_API_KEY")

    if not api_key:
        print("Error: BING_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    results = search(args.query, api_key, args.max_results)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results found for query: '{args.query}'")
            return

        print(f"--- Bing Search Results for '{args.query}' ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet']}")


if __name__ == "__main__":
    main()

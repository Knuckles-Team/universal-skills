#!/usr/bin/env python3
import argparse
import json
import sys

try:
    from ddgs import DDGS
except ImportError:
    print("Error: Missing required dependencies for the 'web-searching' skill.")
    print(
        "Please install them by running: pip install 'universal-skills[web-searching]'"
    )
    sys.exit(1)


def search(query: str, max_results: int = 10):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title"),
                        "link": r.get("href"),
                        "snippet": r.get("body"),
                    }
                )
        return results
    except Exception as e:
        print(f"Error performing DuckDuckGo search: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DuckDuckGo Web Search")
    parser.add_argument("query", help="The search query")
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    results = search(args.query, args.max_results)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results found for query: '{args.query}'")
            return

        print(f"--- DuckDuckGo Search Results for '{args.query}' ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet']}")


if __name__ == "__main__":
    main()

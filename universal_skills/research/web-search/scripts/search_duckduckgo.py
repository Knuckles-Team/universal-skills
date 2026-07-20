#!/usr/bin/env python3
import argparse
import json
import sys

try:
    from http_runtime import fetch_json, validate_search_request
except ImportError:
    print("Error: Missing required dependencies for the 'web-search' skill.")
    print("Please install them by running: pip install 'universal-skills[web-search]'")
    sys.exit(1)


def search(query: str, max_results: int = 10):
    try:
        query, max_results = validate_search_request(query, max_results)
        # DuckDuckGo search API endpoint
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}

        data = fetch_json(url, params=params)
        results = []

        # DuckDuckGo API returns results in 'RelatedTopics' or 'Results'
        # We prioritize 'RelatedTopics' as it often contains more relevant web results
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"]:
                if "FirstURL" in topic and "Text" in topic:
                    results.append(
                        {
                            "title": topic.get("Text"),
                            "link": topic.get("FirstURL"),
                            "snippet": topic.get(
                                "Text"
                            ),  # Use Text as snippet for simplicity
                        }
                    )
                elif "Topics" in topic:  # Handle nested topics
                    for sub_topic in topic["Topics"]:
                        if "FirstURL" in sub_topic and "Text" in sub_topic:
                            results.append(
                                {
                                    "title": sub_topic.get("Text"),
                                    "link": sub_topic.get("FirstURL"),
                                    "snippet": sub_topic.get("Text"),
                                }
                            )
        elif "Results" in data:
            for r in data["Results"]:
                results.append(
                    {
                        "title": r.get("Text"),
                        "link": r.get("FirstURL"),
                        "snippet": r.get("Text"),
                    }
                )
        return results[:max_results]
    except Exception as exc:
        raise RuntimeError("DuckDuckGo search failed") from exc


def main():
    parser = argparse.ArgumentParser(description="DuckDuckGo Web Search")
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

    try:
        results = search(args.query, args.max_results)
    except Exception as exc:
        print(f"Search failed ({type(exc).__name__})", file=sys.stderr)
        sys.exit(1)

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

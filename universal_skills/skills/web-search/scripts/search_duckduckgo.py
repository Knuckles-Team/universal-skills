#!/usr/bin/env python3
import argparse
import json
import sys
import os

try:
    import requests
    from agent_utilities.base_utilities import to_boolean
except ImportError:
    print("Error: Missing required dependencies for the 'web-search' skill.")
    print("Please install them by running: pip install 'universal-skills[web-search]'")
    sys.exit(1)


def search(query: str, max_results: int = 10, ssl_verify: bool = True):
    try:
        # DuckDuckGo search API endpoint
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}

        response = requests.get(url, params=params, verify=ssl_verify)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
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
        return results
    except Exception as e:
        print(f"Error performing DuckDuckGo search: {e}", file=sys.stderr)
        sys.exit(1)


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
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL verification (Use with caution)",
    )

    args = parser.parse_args()

    # Precedence: Env Var SSL_VERIFY > CLI --insecure > Default (True)
    ssl_verify_env = os.getenv("SSL_VERIFY")
    if ssl_verify_env is not None:
        ssl_verify = to_boolean(ssl_verify_env)
    elif args.insecure:
        ssl_verify = False
    else:
        ssl_verify = True

    results = search(args.query, args.max_results, ssl_verify=ssl_verify)

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

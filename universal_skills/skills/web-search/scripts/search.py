#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess


def get_script_path(script_base_name):
    # The dispatcher is in the same directory as the other search scripts
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), script_base_name)


def run_search_script(script_name, query, max_results):
    script_path = get_script_path(script_name)
    cmd = [
        sys.executable,
        script_path,
        "--query",
        query,
        "--max-results",
        str(max_results),
        "--json",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running {script_name}: {e}", file=sys.stderr)
        return None


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
    provider_script = "search_duckduckgo.py"  # Default fallback

    if os.environ.get("SEARXNG_URL"):
        provider_script = "search_searxng.py"
    elif os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CX"):
        provider_script = "search_google.py"
    elif os.environ.get("BING_API_KEY"):
        provider_script = "search_bing.py"

    results = run_search_script(provider_script, args.query, args.max_results)

    if results is None:
        # If the preferred one failed, try DuckDuckGo as final fallback
        if provider_script != "search_duckduckgo.py":
            results = run_search_script(
                "search_duckduckgo.py", args.query, args.max_results
            )

    if results is None:
        print("Error: All search providers failed.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"--- Search Results for '{args.query}' (via {provider_script}) ---")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title')}")
            print(f"   URL: {result.get('link')}")
            print(f"   Snippet: {result.get('snippet')}")


if __name__ == "__main__":
    main()

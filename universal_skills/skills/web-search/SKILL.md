---
name: web-search
description: "Search the web using various providers (DuckDuckGo, Google, Bing, Searxng) to find current information, news, and links. Use when the agent needs up-to-date context from the internet."
categories: [Core]
tags: [web, search, duckduckgo, google, bing, searxng]
---

# Web Search

## Overview
This skill provides access to multiple web search engines. It allows agents to retrieve search results (titles, snippets, and URLs) for a given query, which can be useful for gathering current information, answering questions that require real-time data, or finding relevant references.

## Usage

Use the provided scripts with the `--query` flag.

```bash
python scripts/search.py --query "your search query"
```

You can also use a specific provider directly:

```bash
python scripts/search_duckduckgo.py --query "your search query" --max-results 5 --json
```

## Capabilities/Tools

### Search (`search.py`)
- Automatically searches based off environment variable.
- Executes search queries through the `duckduckgo-search` package as a default.

### DuckDuckGo Search (`search_duckduckgo.py`)
- Free and requires no authentication or API keys.
- Ideal for general web searches when no API keys are configured.
- Executes search queries through the `duckduckgo-search` package.

### Google Search (`search_google.py`)
- Utilizes the Google Custom Search API.
- Requires both `GOOGLE_API_KEY` and `GOOGLE_CX` (Custom Search Engine ID) environment variables.
- Excellent for highly relevant and authoritative results.

### Bing Search (`search_bing.py`)
- Utilizes the Bing Web Search API.
- Requires the `BING_API_KEY` environment variable.
- Great alternative to Google for general and comprehensive web searches.

### Searxng Search (`search_searxng.py`)
- Utilizes a given Searxng instance (public or self-hosted).
- Requires the `SEARXNG_URL` environment variable (e.g., `https://searx.be`).
- A privacy-respecting metasearch engine.

## Best Practices
- Prefer DuckDuckGo if no API keys are available in the environment.
- Use specific search providers securely by providing the required API keys as environment variables.
- Formulate clear and precise queries to obtain the best results.
- Limit the number of search results retrieved per request to avoid unnecessary token usage unless more context is explicitly required.

## Resources
- `scripts/search.py`: Comprehensive web search dispatcher.
- `scripts/search_duckduckgo.py`: DuckDuckGo search script.
- `scripts/search_google.py`: Google Custom Search API script.
- `scripts/search_bing.py`: Bing Web Search API script.
- `scripts/search_searxng.py`: Searxng API script.

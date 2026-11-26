---
name: web-search
domain: research
skill_type: skill
description: >-
  Search the web using various providers (DuckDuckGo, Google, Bing, Searxng) to
  find current information, news, and links. Use when the agent needs up-to-date
  context from the internet.
license: MIT
tags: [web, search, duckduckgo, google, bing, searxng]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
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

### Transport policy

All providers use the meristem outbound-source boundary. TLS verification,
private CA bundles, proxies, approved private hosts, redirect policy, and response
limits come from `AgentConfig`/XDG configuration (`TLS_PROFILE_REF`,
`TLS_CA_BUNDLE_REF`, and `SOURCE_HTTP_*`). Provider scripts do not expose a
`verify=False` or `--insecure` shortcut and do not persist endpoint or credential
material.

## Steps

1. Choose a provider from the environment you have. Verify that `env | grep -E "GOOGLE_API_KEY|GOOGLE_CX|BING_API_KEY|SEARXNG_URL"` lists the variables the chosen provider needs, or choose DuckDuckGo when it prints nothing.
2. Run the search with `python scripts/search.py --query "your search query"`, or a provider script such as `python scripts/search_duckduckgo.py --query "your search query" --max-results 5 --json`. Verify that the output contains titles, snippets and URLs.
3. Narrow the result set by rerunning with a more precise query and a small `--max-results`. Verify that the number of results printed does not exceed the limit you passed.
4. Cite the sources you use. Verify that every URL you quote appears verbatim in the script output, for example with `grep -F "<url>"` on a saved copy.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Google or Bing script errors on authentication | `GOOGLE_API_KEY`, `GOOGLE_CX` or `BING_API_KEY` is missing | Export the missing variable, or switch to `python scripts/search_duckduckgo.py --query "..."` which needs no key. |
| Searxng script cannot connect | `SEARXNG_URL` is unset or points to an unreachable instance | Set `SEARXNG_URL` to a reachable instance such as a self-hosted one and rerun. |
| No results from DuckDuckGo | Rate limiting or the `duckduckgo-search` package is missing | Run `pip install duckduckgo-search` and then use another provider script such as `search_searxng.py`. |
| TLS or private-host error | The outbound policy blocked the endpoint | Set the approved TLS profile or host through `AgentConfig` (`SOURCE_HTTP_*`); there is no `--insecure` option. |

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

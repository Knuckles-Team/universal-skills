---
name: web-fetch
description: Fetch and extract high-fidelity markdown content from a single URL. Supports JavaScript rendering and optional LLM-based information extraction. Use when you need the full content of a specific web page to answer a query or analyze its details.
tags: [web, fetch, markdown, crawl4ai, extraction]
version: '0.6.0'
---

# Web Fetch

## Overview
This skill provides a high-fidelity tool for fetching and extracting content from a single URL. Unlike search, which returns multiple snippets, **Web Fetch** retrieves the entire page content, renders it with JavaScript, and converts it into clean, structured Markdown. It also supports an optional extraction prompt to pull specific data from the page using an LLM.

## Usage

Use the `scripts/fetch.py` script to fetch a page:

```bash
python scripts/fetch.py --url "https://example.com"
```

To extract specific information using an LLM, provide the `--prompt` flag:

```bash
python scripts/fetch.py --url "https://example.com" --prompt "What is the main value proposition mentioned on the page?"
```

For JSON output:

```bash
python scripts/fetch.py --url "https://example.com" --json
```

## Capabilities/Tools

### Fetch (`fetch.py`)
- **JavaScript Rendering**: Uses a headless browser to ensure lazy-loaded content and SPAs are correctly captured.
- **High-Fidelity Markdown**: Leverages `crawl4ai`'s advanced extraction to produce clean, hierarchical Markdown while stripping away noise like headers, footers, and ads.
- **LLM Extraction**: Optionally processes the extracted markdown through an LLM (Claude/GPT) to answer specific questions or extract structured data.

## Best Practices
- **Use for Single Pages**: This tool is optimized for fetching one URL at a time. For broad discovery, use `web-search` first.
- **Prompt Engineering**: When using `--prompt`, provide clear instructions on what specific data points you need to extract from the page.
- **Error Handling**: The tool will report HTTP errors or rendering failures. Always check the output for successfully retrieved content.
- **Privacy & Auth**: This tool fetches public URLs. It does not support authenticated sessions (e.g., login-protected pages).

## Resources
- `scripts/fetch.py`: Main execution script for fetching and extraction.

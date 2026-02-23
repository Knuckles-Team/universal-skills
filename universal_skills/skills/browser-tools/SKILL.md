---
name: browser-tools
description: "Use this skill whenever you need to interact with web pages, perform E2E web application testing, navigate visually, or start a local dev server and test it using Playwright. Excellent for visual QA or fetching dynamic content."
categories: [System & Infrastructure]
tags: [browser, playwright, testing, web, automation, e2e]
---

# Browser Tools

## Overview

This skill combines tools for Browser interactions and Web Application Testing using Playwright.

## Capabilities/Tools

### 1. Webapp Testing (`scripts/with_server.py`)
Start a zero-config local web server (Python `http.server`) and execute tests or commands against it. Useful for running Playwright tests over newly generated HTML.

```bash
# Starts a server in ./public and runs pytest
python scripts/with_server.py --port 8080 --dir ./public -- "pytest tests/e2e"
```

### 2. Playwright CLI (`scripts/playwright_cli.sh`)
Execute basic Playwright CLI commands to inspect, screenshot, or fetch PDF versions of pages. Note: Complex interactions usually require writing an actual Playwright python script.

```bash
# Take a screenshot
bash scripts/playwright_cli.sh screenshot "https://example.com" "example.png"

# Save as PDF
bash scripts/playwright_cli.sh pdf "https://example.com" "example.pdf"
```

## Best Practices
- For full-page visual interaction, write small self-contained `playwright` python scripts to click, type, and extract data, rather than relying solely on the CLI wrapper.
- Use `with_server.py` to assert that locally built React components or simple HTML files correctly render without CORS issues.

---
name: web-fetch
domain: research
skill_type: skill
description: >-
  Compatibility alias for the consolidated web-crawler single-page workflow.
  Use when an existing workflow names web-fetch; prefer web-crawler for new
  fetch, crawl, sitemap, rendered-page, or GraphOS-ingestion tasks.
tags: [web, fetch, compatibility, web-crawler]
license: MIT
metadata:
  version: '1.3.0'
  author: Repository Maintainers
---

# Web Fetch Compatibility Alias

Use `web-crawler` for all new work. This alias keeps existing single-page
commands functional without maintaining a second HTTP, browser, TLS, privacy,
or output stack.

```bash
python scripts/fetch.py --url "https://example.org/page"
python scripts/fetch.py --url "https://example.org/page" --json
```

The command always uses web-crawler's bounded AgentConfig-managed HTTP path.
It validates DNS, redirects, private addresses, TLS profiles, response limits,
and durable output through the same central policy. JSON output contains an
opaque source reference rather than the URL. It does not accept authenticated
sessions, insecure TLS switches, or embedded LLM extraction. Perform analysis
of the sanitized result through the governed agent or GraphOS runtime.

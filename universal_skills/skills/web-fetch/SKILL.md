---
name: web-fetch
domain: research
skill_type: skill
description: >-
  Compatibility alias for the consolidated web-crawler single-page workflow.
  Use when an existing workflow names web-fetch; prefer web-crawler for new
  fetch, crawl, sitemap, rendered-page, or Arbora-ingestion tasks.
tags: [web, fetch, compatibility, web-crawler]
license: MIT
metadata:
  version: '1.7.0'
  author: Knuckles-Team
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
of the sanitized result through the governed agent or Arbora runtime.

## Steps

1. Fetch a single page with `python scripts/fetch.py --url "https://example.org/page"`. Verify that the command exits 0 and prints sanitized page text.
2. Request structured output with `python scripts/fetch.py --url "https://example.org/page" --json`. Verify that the JSON parses, for example with `python scripts/fetch.py --url "https://example.org/page" --json | python3 -m json.tool`, and carries an opaque source reference instead of the URL.
3. Check that the sibling crawler is present with `ls ../web-crawler/scripts/crawl.py`. Verify that the file is listed, since this alias loads it at run time.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `crawler_runtime_unavailable` | The sibling `web-crawler/scripts` folder is missing or is a symlink | Restore the real `web-crawler` skill folder next to `web-fetch` and rerun the command. |
| URL rejected by policy | DNS, redirect or private-address validation failed | Use a public `https` URL, or fetch via `web-crawler` if the target needs different handling. |
| Authenticated or insecure-TLS fetch requested | The alias does not accept sessions or TLS switches | Use the governed agent or Arbora runtime for those needs instead of this alias. |

---
name: web-fetch
domain: research
skill_type: skill
description: >-
  Fetch one page as a cited Document through web-crawler and Arbora
  research.web. Use when a workflow names web-fetch; it forwards one URL.
tags: [web, fetch, compatibility, web-crawler]
license: MIT
metadata:
  version: '1.3.11'
  author: Repository Maintainers
---
# Web Fetch

`scripts/fetch.py` forwards to `web-crawler` with one URL and `max_pages` 1.
It holds no code of its own beyond the forward.

```bash
python scripts/fetch.py --url "https://example.org/page"
python scripts/fetch.py --url "https://example.org/page" --backend archivebox
```

Output and refusals are those of `web-crawler`.

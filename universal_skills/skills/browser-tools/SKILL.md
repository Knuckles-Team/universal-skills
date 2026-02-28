---
name: browser-tools
description: Use when interacting with web pages, automating browser actions, performing E2E web application testing, navigating visually, scraping dynamic content, or starting a local dev server to test against. Triggers include requests to open a website, fill a form, click a button, take a screenshot, scrape dynamic content, test a web app, login to a site, or automate any browser-based task. Do NOT use for fetching static API JSON or simple HTTP requests — use web-search or web-crawler for those.
categories: [System & Infrastructure]
tags: [browser, playwright, testing, web, automation, e2e, agent-browser]
---

# Browser Tools

## Overview

Two approaches for browser automation and web application testing:

1. **`agent-browser` CLI** — Preferred for interactive navigation tasks (snapshot-based, works with any live site)
2. **Playwright scripts** — Preferred for automated E2E test suites against local servers

---

## Approach 1: agent-browser CLI (Interactive Navigation)

### Core Workflow

Every browser automation follows: **Navigate → Snapshot → Interact → Re-snapshot**

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Verify result
```

### Essential Commands

```bash
# Navigation
agent-browser open <url>              # Navigate to URL
agent-browser close                   # Close browser

# Snapshot (get element refs @e1, @e2, ...)
agent-browser snapshot -i             # Interactive elements only (recommended)
agent-browser snapshot -i -C          # Include cursor-interactive elements (divs with onclick)
agent-browser snapshot -s "#selector" # Scope snapshot to CSS selector

# Interaction (always use @refs from snapshot)
agent-browser click @e1               # Click element
agent-browser fill @e2 "text"         # Clear and type text
agent-browser type @e2 "text"         # Type without clearing
agent-browser select @e1 "option"     # Select dropdown value
agent-browser check @e1               # Toggle checkbox
agent-browser press Enter             # Press keyboard key
agent-browser scroll down 500         # Scroll page

# Information
agent-browser get text @e1            # Get element text content
agent-browser get url                 # Get current URL
agent-browser get title               # Get page title

# Waiting
agent-browser wait @e1                # Wait for element to appear
agent-browser wait --load networkidle # Wait for network to settle
agent-browser wait --url "**/path"    # Wait for URL pattern
agent-browser wait 2000               # Wait fixed milliseconds

# Capture
agent-browser screenshot              # Screenshot to temp dir
agent-browser screenshot --full       # Full-page screenshot
agent-browser screenshot --annotate   # Annotated screenshot with numbered element labels
agent-browser pdf output.pdf          # Save page as PDF
```

### Important: Ref Lifecycle

Refs (`@e1`, `@e2`, ...) are **invalidated** whenever the page changes. Always re-snapshot after:
- Clicking links or buttons that navigate
- Form submissions
- Dynamic content loading (modals, dropdowns)

```bash
agent-browser click @e5     # Navigates to new page
agent-browser snapshot -i   # MUST re-snapshot before using any refs
agent-browser click @e1     # Use new refs
```

### Common Patterns

**Form Submission:**
```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser click @e4
agent-browser wait --load networkidle
```

**Data Extraction:**
```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5
agent-browser get text body > /tmp/page.txt
```

**Annotated Screenshots (when element labels unclear):**
```bash
agent-browser screenshot --annotate
# Output: image path + legend: [1] @e1 button "Submit", [2] @e2 link "Home"
agent-browser click @e1  # Use ref from annotated screenshot
```

**Semantic Locators (when @refs unavailable):**
```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
```

---

## Approach 2: Playwright Scripts (E2E Testing Against Local Servers)

### Decision Tree

```
Task → Is it a static HTML file?
  ├─ Yes → Read HTML directly to identify selectors
  │         ├─ Success → Write Playwright script with found selectors
  │         └─ Fails → Treat as dynamic (below)
  │
  └─ No (dynamic app) → Is the server already running?
      ├─ No → Run with_server.py (see below) + write Playwright script
      └─ Yes → Reconnaissance-then-action:
          1. Navigate and wait for networkidle
          2. Screenshot or inspect DOM
          3. Identify selectors from rendered state
          4. Execute actions with discovered selectors
```

### Using `scripts/with_server.py`

Always run `--help` first to see options. Use for managing server lifecycle:

```bash
# Single server + run automation
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py

# Multiple servers (backend + frontend)
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

### Playwright Script Pattern

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Always headless
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # CRITICAL: wait for JS to execute

    # Reconnaissance: take screenshot or inspect DOM first
    page.screenshot(path='/tmp/inspect.png', full_page=True)

    # Then interact using discovered selectors
    page.fill('input[type="email"]', 'user@example.com')
    page.click('button[type="submit"]')

    browser.close()
```

### Best Practices

- **Always** `wait_for_load_state('networkidle')` before inspecting DOM on dynamic apps
- Use semantic selectors: `text=`, `role=`, CSS, or IDs — avoid brittle XPath
- Add explicit waits with `page.wait_for_selector()` for slow elements
- Use `scripts/with_server.py` with `--help` first — do not read its source unless necessary
- For `agent-browser`, always close the session when done: `agent-browser close`

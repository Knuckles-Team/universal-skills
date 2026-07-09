---
name: agent-browser
domain: agent-tools
skill_type: skill
description: >-
  Browser automation CLI for AI agents using the agent-browser tool. Use when the
  user needs to interact with websites including navigating pages, filling forms,
  clicking buttons, taking screenshots, extracting data, testing web apps, or
  automating any browser task. Triggers include requests to "open a website",
  "fill out a form", "click a button", "take a screenshot", "scrape data from a
  page", "test this web app", "login to a site", "automate browser actions", or
  any task requiring programmatic web interaction.
license: MIT
tags: [browser, automation, playwright, web-scraping, testing, screenshots]
metadata:
  version: '1.1.0'
  author: Genius
---
# Browser Automation with agent-browser

## Overview

Automate browser interactions using the `agent-browser` CLI tool. Every automation follows a consistent navigate → snapshot → interact → re-snapshot pattern. The browser persists between commands via a background daemon, making command chaining efficient.

---

## Setup — run this FIRST (self-installing)

The `agent-browser` CLI is **not preinstalled**. This skill ships `bootstrap.sh`,
which is idempotent — run it at the start of every task; it no-ops if already set up:

```bash
# install the CLI + ensure Chromium, and export PATH/PNPM_HOME/PLAYWRIGHT_BROWSERS_PATH
source "$(dirname "$0")/bootstrap.sh" 2>/dev/null || source ./bootstrap.sh
# (the skill dir is printed by `agent-browser skills path` once installed)
```

If you only need the binary on PATH (no env persistence), run it as a subprocess:
`bash <skill-dir>/bootstrap.sh`.

### What bootstrap handles (and why — validated 2026-06-10)

- **Install with `pnpm`, not `npm`.** The bundled npm (Python `nodejs_wheel`) is
  broken here. `pnpm add -g agent-browser` (public npm registry) works. pnpm prints
  *"Ignored build scripts"* — harmless. The bin lands in `$PNPM_HOME`
  (default `~/.local/share/pnpm`), which bootstrap adds to `PATH`.
- **Playwright Chromium is usually already cached** at `~/.cache/ms-playwright`
  (`PLAYWRIGHT_BROWSERS_PATH`). Bootstrap only downloads it if absent.

## Headless server / SSH environments (e.g. this homelab)

- **Headless is the default** — do *not* pass `--headed` on a server with no display.
- **Containers need `--no-sandbox`.** Bootstrap sets `AGENT_BROWSER_ARGS=--no-sandbox`.
  Use a **single** flag here: multiple space-split flags in `AGENT_BROWSER_ARGS` trip
  Chromium's `Multiple targets are not supported in headless mode`.
- **Internal / plain-HTTP sites are blocked by default.** Homelab `*.arpa` hosts
  (served by Caddy over **http**) — and any pure-http site — return
  `ERR_BLOCKED_BY_CLIENT` and land on `chrome-error://`. Cause: Chromium's
  **HTTPS-Upgrade** auto-upgrades `http`→`https` and won't fall back. `--no-sandbox`
  alone does NOT fix this, and the needed `--disable-features` flag can't be added via
  `AGENT_BROWSER_ARGS` (see the multi-flag bug above).

  **Working fix — pre-launch Chromium with the flags, then attach over CDP:**

  ```bash
  bash <skill-dir>/bootstrap.sh --connect      # launches Chromium + `agent-browser connect`
  agent-browser open http://twenty.arpa/       # now loads (verified -> /welcome)
  ```

  Equivalent manual form:

  ```bash
  CHROME=$(find ~/.cache/ms-playwright -name chrome -path '*chromium-*' | head -1)
  "$CHROME" --headless=new --no-sandbox --disable-gpu \
    --disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2 \
    --remote-debugging-port=9222 --user-data-dir="$(mktemp -d)" &
  agent-browser connect 9222
  ```

- **Self-signed HTTPS:** add `--ignore-https-errors` on `open`.

## Daemon hygiene

- Reset the persistent browser with **`agent-browser close --all`**.
- **Do NOT `pkill -f agent-browser`** — the pattern matches your own shell/command
  line and kills the session (seen as exit 144). Kill a *pre-launched* Chromium by
  its unique `--user-data-dir` path instead (e.g. `pkill -f /tmp/agent-browser-prof`).
- A stale daemon is a common cause of `Multiple targets are not supported in headless
  mode`; `close --all` (and, if needed, killing the CDP Chromium) clears it.

---

## Core Workflow

Every browser automation task follows this pattern:

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i` (get interactive element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Check result
```

---

## Command Reference

```bash
# Navigation
agent-browser open <url>              # Navigate (aliases: goto, navigate)
agent-browser close                   # Close browser

# Snapshot
agent-browser snapshot -i             # Interactive elements with refs (recommended)
agent-browser snapshot -i -C          # Include cursor-interactive elements (divs with onclick)
agent-browser snapshot -s "#selector" # Scope to CSS selector

# Interaction (use @refs from snapshot)
agent-browser click @e1               # Click element
agent-browser click @e1 --new-tab     # Click and open in new tab
agent-browser fill @e2 "text"         # Clear and type text
agent-browser type @e2 "text"         # Type without clearing
agent-browser select @e1 "option"     # Select dropdown option
agent-browser check @e1               # Check checkbox
agent-browser press Enter             # Press key
agent-browser scroll down 500         # Scroll page

# Get information
agent-browser get text @e1            # Get element text
agent-browser get url                 # Get current URL
agent-browser get title               # Get page title

# Wait
agent-browser wait @e1                # Wait for element
agent-browser wait --load networkidle # Wait for network idle
agent-browser wait --url "**/page"    # Wait for URL pattern
agent-browser wait 2000               # Wait milliseconds

# Capture
agent-browser screenshot              # Screenshot to temp dir
agent-browser screenshot --full       # Full page screenshot
agent-browser screenshot --annotate   # Annotated screenshot with numbered labels
agent-browser pdf output.pdf          # Save as PDF

# Diff (compare page states)
agent-browser diff snapshot                          # Compare current vs last snapshot
agent-browser diff snapshot --baseline before.txt    # Compare current vs saved file
agent-browser diff screenshot --baseline before.png  # Visual pixel diff
agent-browser diff url <url1> <url2>                 # Compare two pages
```

---

## Common Patterns

### Form Submission

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### Authentication with State Persistence

```bash
# Login once and save state
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# Reuse in future sessions
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### Session Persistence

```bash
# Auto-save/restore cookies and localStorage across browser restarts
agent-browser --session-name myapp open https://app.example.com/login
# ... login flow ...
agent-browser close  # State auto-saved to ~/.agent-browser/sessions/

# Next time, state is auto-loaded
agent-browser --session-name myapp open https://app.example.com/dashboard
```

### Data Extraction

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5            # Get specific element text
agent-browser get text body > page.txt  # Get all page text

# JSON output for parsing
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### Parallel Sessions

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

---

## Command Chaining

Commands can be chained with `&&` in a single shell invocation. The browser persists between commands, so chaining is safe and efficient.

```bash
# Chain open + wait + snapshot in one call
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser snapshot -i

# Navigate and capture
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser screenshot page.png
```

**When to chain:** Use `&&` when intermediate output isn't needed (e.g., open + wait + screenshot). Run commands separately when parsing output first (e.g., snapshot to discover refs, then interact using those refs).

---

## Ref Lifecycle

Refs (`@e1`, `@e2`, etc.) are invalidated when the page changes. Always re-snapshot after:

- Clicking links or buttons that navigate
- Form submissions
- Dynamic content loading (dropdowns, modals)

```bash
agent-browser click @e5              # Navigates to new page
agent-browser snapshot -i            # MUST re-snapshot
agent-browser click @e1              # Use new refs
```

---

## Annotated Screenshots (Vision Mode)

Use `--annotate` to take a screenshot with numbered labels overlaid on interactive elements. Each label `[N]` maps to ref `@eN`. This also caches refs, so interactions can begin immediately without a separate snapshot.

```bash
agent-browser screenshot --annotate
# Output includes the image path and a legend:
#   [1] @e1 button "Submit"
#   [2] @e2 link "Home"
#   [3] @e3 textbox "Email"
agent-browser click @e2              # Click using ref from annotated screenshot
```

Use annotated screenshots when:
- The page has unlabeled icon buttons or visual-only elements
- Canvas or chart elements are present (invisible to text snapshots)
- Spatial reasoning about element positions is needed

---

## Semantic Locators (Alternative to Refs)

When refs are unavailable or unreliable, use semantic locators:

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```

---

## JavaScript Evaluation

Use `eval` to run JavaScript in the browser context. Use `--stdin` or `-b` for complex expressions to avoid shell quoting issues.

```bash
# Simple expressions
agent-browser eval 'document.title'
agent-browser eval 'document.querySelectorAll("img").length'

# Complex JS: use --stdin with heredoc (recommended)
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll("img"))
    .filter(i => !i.alt)
    .map(i => ({ src: i.src.split("/").pop(), width: i.width }))
)
EVALEOF

# Base64 encoding (avoids all shell escaping issues)
agent-browser eval -b "$(echo -n 'Array.from(document.querySelectorAll("a")).map(a => a.href)' | base64)"
```

---

## Timeouts and Slow Pages

```bash
# Wait for network activity to settle (best for slow pages)
agent-browser wait --load networkidle

# Wait for a specific element to appear
agent-browser wait "#content"

# Wait for a URL pattern (useful after redirects)
agent-browser wait --url "**/dashboard"

# Wait for a JavaScript condition
agent-browser wait --fn "document.readyState === 'complete'"

# Fixed duration as a last resort
agent-browser wait 5000
```

---

## Diffing (Verifying Changes)

Use `diff snapshot` after an action to verify it had the intended effect:

```bash
# Typical workflow: snapshot → action → diff
agent-browser snapshot -i          # Take baseline snapshot
agent-browser click @e2            # Perform action
agent-browser diff snapshot        # See what changed

# Visual regression testing
agent-browser screenshot baseline.png
# ... changes made ...
agent-browser diff screenshot --baseline baseline.png

# Compare staging vs production
agent-browser diff url https://staging.example.com https://prod.example.com --screenshot
```

---

## Best Practices

- **Always re-snapshot after navigation** — refs become invalid when the page changes
- **Use `wait --load networkidle`** after opening slow or SPA-based pages
- **Use named sessions** when running concurrent agents to avoid conflicts
- **Always close sessions** when done to avoid leaked browser processes
- **Prefer `--stdin` for complex JavaScript** to avoid shell escaping issues

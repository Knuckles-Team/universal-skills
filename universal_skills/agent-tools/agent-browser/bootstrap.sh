#!/usr/bin/env bash
# agent-browser self-bootstrap for headless / server (SSH) environments.
#
# Idempotent — safe to source or run at the start of every agent-browser task.
# It (1) installs the `agent-browser` CLI if missing, (2) ensures Playwright's
# Chromium is available, and (3) — with `--connect` — launches Chromium with the
# flags this environment needs and attaches agent-browser to it over CDP.
#
# Why this exists (validated findings, 2026-06-10):
#   * The bundled npm (python `nodejs_wheel`) is BROKEN here — use `pnpm`.
#   * `agent-browser` is the PUBLIC npm package (not a private/own build).
#   * Playwright Chromium is normally already cached under ~/.cache/ms-playwright.
#   * Headless is the DEFAULT; this is a container, so Chromium needs --no-sandbox.
#   * Plain-HTTP sites (homelab *.arpa served by Caddy over http, or any pure-http
#     site) are blocked by Chromium's HTTPS-Upgrade as ERR_BLOCKED_BY_CLIENT and
#     land on chrome-error://. --no-sandbox ALONE is not enough; and passing extra
#     flags via AGENT_BROWSER_ARGS (space-split) trips Chromium's
#     "Multiple targets are not supported in headless mode". The reliable fix is to
#     pre-launch Chromium with the flags and `agent-browser connect` to it (below).
#
# Usage:
#   source bootstrap.sh            # install + export env (PATH/PNPM_HOME/PLAYWRIGHT_*)
#   bash   bootstrap.sh            # same, as a subprocess (env won't persist)
#   bash   bootstrap.sh --connect  # also launch Chromium + connect (for *.arpa/http)
#   AB_CDP_PORT=9333 bash bootstrap.sh --connect   # custom CDP port

set -uo pipefail

export PNPM_HOME="${PNPM_HOME:-$HOME/.local/share/pnpm}"
export PATH="$PNPM_HOME:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
mkdir -p "$PNPM_HOME"

# --- 1. install the CLI (pnpm; the bundled npm is broken) -------------------
if ! command -v agent-browser >/dev/null 2>&1; then
  if ! command -v pnpm >/dev/null 2>&1; then
    echo "ERROR: neither agent-browser nor pnpm found; cannot bootstrap." >&2
    return 1 2>/dev/null || exit 1
  fi
  echo "[agent-browser] installing CLI via pnpm (public npm registry)…"
  pnpm add -g agent-browser --registry=https://registry.npmjs.org/ \
    || { echo "ERROR: pnpm add -g agent-browser failed." >&2; return 1 2>/dev/null || exit 1; }
fi
echo "[agent-browser] CLI: $(agent-browser --version 2>/dev/null || echo '?')"

# --- 2. ensure a Chromium build is present ----------------------------------
find_chrome() {
  find "$PLAYWRIGHT_BROWSERS_PATH" -maxdepth 3 -type f -name chrome -path '*chromium-*' 2>/dev/null | head -1
}
CHROME_BIN="$(find_chrome)"
if [ -z "$CHROME_BIN" ]; then
  echo "[agent-browser] Chromium not cached; installing via Playwright…"
  pnpm dlx playwright install chromium >/dev/null 2>&1 || playwright install chromium >/dev/null 2>&1 || true
  CHROME_BIN="$(find_chrome)"
fi
echo "[agent-browser] Chromium: ${CHROME_BIN:-NOT FOUND}"

# Single-arg only — multiple space-split flags here break headless launch.
export AGENT_BROWSER_ARGS="${AGENT_BROWSER_ARGS:---no-sandbox}"

# --- 3. optional: launch Chromium with the right flags + connect via CDP ----
# Required to load plain-HTTP / *.arpa (homelab) sites (see header note).
if [ "${1:-}" = "--connect" ]; then
  PORT="${AB_CDP_PORT:-9222}"
  if ! curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    [ -n "$CHROME_BIN" ] || { echo "ERROR: no Chromium to launch." >&2; return 1 2>/dev/null || exit 1; }
    PROF="$(mktemp -d /tmp/agent-browser-prof.XXXXXX)"
    echo "[agent-browser] launching Chromium (headless, --no-sandbox, HTTPS-Upgrade off) on CDP :${PORT}…"
    "$CHROME_BIN" --headless=new --no-sandbox --disable-gpu \
      --disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2 \
      --remote-debugging-port="${PORT}" --user-data-dir="${PROF}" \
      >/tmp/agent-browser-chrome.log 2>&1 &
    for _ in $(seq 1 30); do
      curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1 && break; sleep 0.5
    done
  fi
  if curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    agent-browser connect "${PORT}" >/dev/null 2>&1 \
      && echo "[agent-browser] connected to CDP :${PORT} — internal http/*.arpa sites will load." \
      || echo "WARN: 'agent-browser connect ${PORT}' failed." >&2
  else
    echo "ERROR: Chromium did not come up on CDP :${PORT} (see /tmp/agent-browser-chrome.log)." >&2
  fi
fi

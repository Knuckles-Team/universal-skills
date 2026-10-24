#!/usr/bin/env bash
# agent-browser self-bootstrap for headless / server (SSH) environments.
#
# Idempotent bootstrap for an already provisioned agent-browser/Chromium runtime.
# Package installation, browser sandbox disablement, and HTTP downgrade support
# are explicit opt-ins; secure defaults never fetch unpinned code or weaken the
# browser process.
#
# Usage:
#   source bootstrap.sh            # install + export env (PATH/PNPM_HOME/PLAYWRIGHT_*)
#   bash   bootstrap.sh            # same, as a subprocess (env won't persist)
#   bash   bootstrap.sh --connect  # also launch Chromium + connect over loopback
#   AB_CDP_PORT=9333 bash bootstrap.sh --connect   # custom CDP port

set -uo pipefail

export PNPM_HOME="${PNPM_HOME:-$HOME/.local/share/pnpm}"
export PATH="$PNPM_HOME:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
mkdir -p "$PNPM_HOME"

# --- 1. install the CLI (pnpm; the bundled npm is broken) -------------------
if ! command -v agent-browser >/dev/null 2>&1; then
  if [ "${AGENT_BROWSER_ALLOW_BOOTSTRAP_INSTALL:-0}" != "1" ]; then
    echo "ERROR: agent-browser is not installed; bootstrap installation is disabled." >&2
    return 1 2>/dev/null || exit 1
  fi
  if ! command -v pnpm >/dev/null 2>&1 || [ -z "${AGENT_BROWSER_PACKAGE_SPEC:-}" ]; then
    echo "ERROR: configure pnpm and a pinned AGENT_BROWSER_PACKAGE_SPEC." >&2
    return 1 2>/dev/null || exit 1
  fi
  echo "[agent-browser] installing the configured pinned CLI package…"
  pnpm add -g "$AGENT_BROWSER_PACKAGE_SPEC" \
    || { echo "ERROR: pnpm add -g agent-browser failed." >&2; return 1 2>/dev/null || exit 1; }
fi
echo "[agent-browser] CLI: $(agent-browser --version 2>/dev/null || echo '?')"

# --- 2. ensure a Chromium build is present ----------------------------------
find_chrome() {
  find "$PLAYWRIGHT_BROWSERS_PATH" -maxdepth 3 -type f -name chrome -path '*chromium-*' 2>/dev/null | head -1
}
CHROME_BIN="$(find_chrome)"
if [ -z "$CHROME_BIN" ]; then
  if [ "${AGENT_BROWSER_ALLOW_BROWSER_INSTALL:-0}" = "1" ] \
    && [ -n "${PLAYWRIGHT_PACKAGE_SPEC:-}" ] \
    && command -v pnpm >/dev/null 2>&1; then
    echo "[agent-browser] installing Chromium through the configured pinned Playwright package…"
    pnpm dlx "$PLAYWRIGHT_PACKAGE_SPEC" install chromium >/dev/null 2>&1 || true
    CHROME_BIN="$(find_chrome)"
  fi
fi
if [ -n "$CHROME_BIN" ]; then
  echo "[agent-browser] Chromium available"
else
  echo "[agent-browser] Chromium unavailable"
fi

# Browser sandbox disablement is never implicit.
if [ "${AGENT_BROWSER_DISABLE_SANDBOX:-0}" = "1" ]; then
  export AGENT_BROWSER_ARGS="${AGENT_BROWSER_ARGS:---no-sandbox}"
fi

# --- 3. optional: launch Chromium with the right flags + connect via CDP ----
if [ "${1:-}" = "--connect" ]; then
  PORT="${AB_CDP_PORT:-9222}"
  RUNTIME_ROOT="${XDG_RUNTIME_DIR:-${TMPDIR:-/tmp}}/agent-browser-${UID:-0}"
  mkdir -p "$RUNTIME_ROOT"
  chmod 700 "$RUNTIME_ROOT"
  CHROME_LOG="$RUNTIME_ROOT/chromium.log"
  if ! curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    [ -n "$CHROME_BIN" ] || { echo "ERROR: no Chromium to launch." >&2; return 1 2>/dev/null || exit 1; }
    PROF="$(mktemp -d "$RUNTIME_ROOT/profile.XXXXXX")"
    browser_flags=(
      --headless=new
      --disable-gpu
      --remote-debugging-address=127.0.0.1
      --remote-debugging-port="${PORT}"
      --user-data-dir="${PROF}"
    )
    if [ "${AGENT_BROWSER_DISABLE_SANDBOX:-0}" = "1" ]; then
      browser_flags+=(--no-sandbox)
    fi
    if [ "${AGENT_BROWSER_ALLOW_INSECURE_HTTP:-0}" = "1" ]; then
      browser_flags+=(--disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2)
    fi
    echo "[agent-browser] launching Chromium over a loopback-only CDP endpoint…"
    "$CHROME_BIN" "${browser_flags[@]}" >"$CHROME_LOG" 2>&1 &
    for _ in $(seq 1 30); do
      curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1 && break; sleep 0.5
    done
  fi
  if curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    agent-browser connect "${PORT}" >/dev/null 2>&1 \
      && echo "[agent-browser] connected to the loopback CDP endpoint." \
      || echo "WARN: agent-browser CDP connection failed." >&2
  else
    echo "ERROR: Chromium did not start; diagnostic output is in the private runtime directory." >&2
  fi
fi

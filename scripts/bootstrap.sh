#!/usr/bin/env bash
# One-command contributor setup from a fresh clone (local, Claude Code on the
# web, and the hosted CI workflow all run this same script).
#
#   scripts/bootstrap.sh    uv >= 0.9, pinned Python, locked .venv, git hooks
#
# Idempotent and non-interactive. Afterwards:
#   uvx pre-commit run --all-files
#   uv run --frozen --no-sync pytest tests -m "not slow"
set -euo pipefail

cd "$(dirname "$0")/.."

case "${1:-}" in
  '') ;;
  -h | --help) sed -n '2,9p' "$0"; exit 0 ;;
  *) echo "unknown argument: $1" >&2; exit 2 ;;
esac

log() { printf 'bootstrap: %s\n' "$*"; }
export PATH="$HOME/.local/bin:$PATH"

# uv older than 0.9 cannot download current CPython patch releases.
uv_minor() { uv --version 2>/dev/null | awk '{split($2, v, "."); print v[1] * 1000 + v[2]}'; }
if ! command -v uv >/dev/null 2>&1 || [[ "$(uv_minor)" -lt 9 ]]; then
  log "installing a current uv"
  python3 -m pip install --quiet --user --upgrade "uv>=0.9" \
    || curl -LsSf https://astral.sh/uv/install.sh | sh
fi
python_version="$(tr -d '[:space:]' < .python-version)"
log "Python ${python_version} (uv $(uv --version | awk '{print $2}'))"
uv python install "$python_version"

# The tests exercise skill scripts across every optional extra.
log "syncing .venv from uv.lock (all extras)"
uv sync --frozen --python "$python_version" --all-extras

log "installing pre-commit and pre-push hooks"
uvx pre-commit install --hook-type pre-commit --hook-type pre-push >/dev/null

log "done"

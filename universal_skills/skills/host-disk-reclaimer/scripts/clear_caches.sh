#!/usr/bin/env bash
# Clear regenerable package & tool caches. SAFE: every item is re-downloaded or
# regenerated on next use. Does NOT touch source, venvs, or application data.
#
# Usage: clear_caches.sh [REPO_ROOT]
#   REPO_ROOT (optional): sweep per-repo tool caches (__pycache__, .mypy_cache,
#   .ruff_cache, .pytest_cache) under this tree too.
set -uo pipefail

echo "## Package download/build caches"
command -v uv >/dev/null 2>&1 && { echo -n "  uv:  "; uv cache clean 2>&1 | tail -1; }
python3 -m pip cache purge 2>&1 | sed 's/^/  pip: /' | tail -1 || true
for d in "$HOME/.cache/torch" "$HOME/.cache/pre-commit" "$HOME/.cache/pip"; do
  [ -d "$d" ] && rm -rf "$d" && echo "  removed $d"
done

ROOT="${1:-}"
if [ -n "$ROOT" ] && [ -d "$ROOT" ]; then
  echo "## Per-repo tool caches under $ROOT"
  find "$ROOT" -type d \
       \( -name __pycache__ -o -name .mypy_cache -o -name .ruff_cache -o -name .pytest_cache -o -name .hypothesis \) \
       -prune -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null
  echo "  removed __pycache__ / .mypy_cache / .ruff_cache / .pytest_cache / .hypothesis"
fi
echo "Done. Note: pre-commit re-installs hook envs on the next run (first run is slower)."

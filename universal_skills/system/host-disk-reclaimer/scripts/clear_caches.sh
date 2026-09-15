#!/usr/bin/env bash
# Preview or clear regenerable package and per-repository tool caches.
# The default is a read-only dry-run. Deletion requires an explicit --apply.
#
# Usage: clear_caches.sh [--apply] [REPO_ROOT]
set -euo pipefail

APPLY=false
ROOT=""
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=true ;;
    --help|-h)
      echo "usage: clear_caches.sh [--apply] [REPO_ROOT]"
      exit 0
      ;;
    --*)
      echo "unknown option: $arg" >&2
      exit 2
      ;;
    *)
      if [ -n "$ROOT" ]; then
        echo "only one REPO_ROOT may be supplied" >&2
        exit 2
      fi
      ROOT="$arg"
      ;;
  esac
done

canonical_dir() {
  python3 - "$1" <<'PY'
import os
import sys

path = sys.argv[1]
if not os.path.isdir(path) or os.path.islink(path):
    raise SystemExit(1)
print(os.path.realpath(path))
PY
}

dir_bytes() {
  du -sB1 --one-file-system -- "$1" 2>/dev/null | awk '{print $1}'
}

HOME_REAL="$(python3 - "$HOME" <<'PY'
import os
import sys

print(os.path.realpath(sys.argv[1]))
PY
)"

remove_known_cache() {
  requested="$1"
  [ -d "$requested" ] || return 0
  cache_path="$(canonical_dir "$requested")" || {
    echo "  refused non-directory or symlink: $requested" >&2
    return 1
  }
  case "$cache_path" in
    "$HOME_REAL/.cache/uv"|"$HOME_REAL/.cache/torch"|\
    "$HOME_REAL/.cache/pre-commit"|"$HOME_REAL/.cache/pip") ;;
    *)
      echo "  refused path outside the exact cache allowlist: $cache_path" >&2
      return 1
      ;;
  esac
  size="$(dir_bytes "$cache_path")" || size="unknown"
  if $APPLY; then
    python3 - "$cache_path" <<'PY'
import os
import shutil
import sys

path = sys.argv[1]
if os.path.islink(path) or not os.path.isdir(path):
    raise SystemExit(f"refusing unsafe cache path: {path}")
shutil.rmtree(path)
PY
    echo "  removed $cache_path (${size:-unknown} bytes)"
  else
    echo "  would remove $cache_path (${size:-unknown} bytes)"
  fi
}

echo "## Package download/build caches"
for cache_dir in "$HOME/.cache/uv" "$HOME/.cache/torch" \
  "$HOME/.cache/pre-commit" "$HOME/.cache/pip"; do
  remove_known_cache "$cache_dir"
done

if [ -n "$ROOT" ]; then
  ROOT="$(canonical_dir "$ROOT")" || {
    echo "REPO_ROOT must be an existing, non-symlink directory" >&2
    exit 2
  }
  case "$ROOT" in
    /|/home|/var|/usr|/opt)
      echo "refusing unsafe broad REPO_ROOT: $ROOT" >&2
      exit 2
      ;;
  esac

  echo "## Per-repo tool caches under $ROOT"
  count=0
  while IFS= read -r -d '' cache_path; do
    case "$(basename "$cache_path")" in
      __pycache__|.mypy_cache|.ruff_cache|.pytest_cache|.hypothesis) ;;
      *)
        echo "  refused unexpected cache path: $cache_path" >&2
        exit 1
        ;;
    esac
    case "$cache_path" in
      "$ROOT"/*) ;;
      *)
        echo "  refused path outside REPO_ROOT: $cache_path" >&2
        exit 1
        ;;
    esac
    count=$((count + 1))
    if $APPLY; then
      python3 - "$cache_path" <<'PY'
import os
import shutil
import sys

path = sys.argv[1]
if os.path.islink(path) or not os.path.isdir(path):
    raise SystemExit(f"refusing unsafe cache path: {path}")
shutil.rmtree(path)
PY
      echo "  removed $cache_path"
    else
      echo "  would remove $cache_path"
    fi
  done < <(
    find "$ROOT" -xdev -type d \
      \( -name __pycache__ -o -name .mypy_cache -o -name .ruff_cache \
         -o -name .pytest_cache -o -name .hypothesis \) \
      -prune -print0 2>/dev/null
  )
  echo "  candidate directories: $count"
fi

if $APPLY; then
  echo "Applied cache cleanup. Re-measure the constrained filesystem."
else
  echo "Dry-run only; nothing was deleted. Re-run with --apply after review."
fi

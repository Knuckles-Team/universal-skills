#!/usr/bin/env bash
# Preview or consolidate per-package virtualenvs into one shared environment.
# The default is a dry-run. --apply installs a missing editable package first and
# removes only its exact, verified old venv after the shared import succeeds.
#
# Usage: consolidate_venvs.sh <SHARED_VENV> <PACKAGES_ROOT> [--apply]
set -euo pipefail

SHARED_INPUT="${1:?shared venv path}"
ROOT_INPUT="${2:?packages root}"
MODE="${3:-}"
if [ -n "$MODE" ] && [ "$MODE" != "--apply" ]; then
  echo "third argument must be --apply" >&2
  exit 2
fi
APPLY=false
if [ "$MODE" = "--apply" ]; then
  APPLY=true
fi

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

SHARED="$(canonical_dir "$SHARED_INPUT")" || {
  echo "shared venv must be an existing, non-symlink directory" >&2
  exit 2
}
ROOT="$(canonical_dir "$ROOT_INPUT")" || {
  echo "packages root must be an existing, non-symlink directory" >&2
  exit 2
}
case "$ROOT" in
  /|/home|/var|/usr|/opt)
    echo "refusing unsafe broad packages root: $ROOT" >&2
    exit 2
    ;;
esac

PY="$SHARED/bin/python"
UV="${UV:-uv}"
[ -x "$PY" ] || { echo "shared venv python not found: $PY"; exit 1; }

echo "shared venv: $("$PY" --version 2>&1)"
missing=0
declare -a removable=()

for package_dir in "$ROOT"/*/; do
  [ -e "$package_dir/pyproject.toml" ] || continue
  module="$(basename "$package_dir" | tr '-' '_')"
  ready=false
  if "$PY" -c 'import importlib.util,sys;sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)' "$module" 2>/dev/null; then
    ready=true
  else
    missing=$((missing + 1))
    echo "  missing from shared venv: $(basename "$package_dir") ($module)"
    if $APPLY; then
      if "$UV" pip install -e "$package_dir" --no-deps --python "$PY" >/dev/null 2>&1 \
        && "$PY" -c 'import importlib.util,sys;sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)' "$module" 2>/dev/null; then
        ready=true
        echo "    -> installed editable and verified import"
      else
        echo "    -> install/import verification failed; keeping its venv"
      fi
    fi
  fi

  for candidate in "$package_dir/.venv" "$package_dir"/.venv31*; do
    [ -d "$candidate" ] || continue
    if [ -L "$candidate" ]; then
      echo "  refused symlink venv: $candidate" >&2
      continue
    fi
    venv="$(canonical_dir "$candidate")" || continue
    case "$venv" in
      "$ROOT"/*/.venv|"$ROOT"/*/.venv31*) ;;
      *)
        echo "  refused unexpected venv path: $venv" >&2
        continue
        ;;
    esac
    [ "$venv" = "$SHARED" ] && continue
    if $ready; then
      removable+=("$venv")
      echo "  candidate: $venv"
    else
      echo "  keep until shared import verifies: $venv"
    fi
  done
done

echo "missing packages before apply: $missing"
if $APPLY; then
  removed=0
  for venv in "${removable[@]}"; do
    python3 - "$ROOT" "$venv" <<'PY'
import os
import shutil
import sys

root, path = map(os.path.realpath, sys.argv[1:])
name = os.path.basename(path)
if os.path.islink(path) or not os.path.isdir(path):
    raise SystemExit(f"refusing unsafe venv path: {path}")
if os.path.commonpath((root, path)) != root or not (
    name == ".venv" or name.startswith(".venv31")
):
    raise SystemExit(f"refusing path outside exact venv policy: {path}")
shutil.rmtree(path)
PY
    removed=$((removed + 1))
    echo "  removed $venv"
  done
  echo "removed $removed verified redundant venv directories"
else
  echo "Dry-run only; nothing was installed or removed. Re-run with --apply after review."
fi

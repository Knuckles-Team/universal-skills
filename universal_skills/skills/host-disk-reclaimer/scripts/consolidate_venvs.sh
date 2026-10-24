#!/usr/bin/env bash
# Consolidate many per-repo .venv directories into ONE shared venv. For each
# package missing from the shared venv it installs it editable (--no-deps, since
# the shared venv already carries the common dependency closure), then removes
# the now-redundant per-repo .venv dirs.
#
# Usage: consolidate_venvs.sh <SHARED_VENV> <PACKAGES_ROOT> [--apply]
#   SHARED_VENV   : path to the one venv to keep (e.g. "$AGENT_UTILITIES_WORKSPACE_ROOT/.venv")
#   PACKAGES_ROOT : dir whose immediate <child>/ entries are packages with a
#                   pyproject.toml and a per-repo .venv (e.g. .../agents)
#   default is a DRY-RUN (reports missing pkgs only); --apply makes changes.
set -uo pipefail
SHARED="${1:?shared venv path}"; ROOT="${2:?packages root}"; APPLY="${3:-}"
PY="$SHARED/bin/python"; UV="${UV:-uv}"
[ -x "$PY" ] || { echo "shared venv python not found: $PY"; exit 1; }

echo "shared venv: $("$PY" --version 2>&1)  | editable pkgs: $(ls "$SHARED"/lib/*/site-packages/__editable__*.pth 2>/dev/null | wc -l)"

missing=0
for d in "$ROOT"/*/; do
  [ -e "$d/pyproject.toml" ] || continue
  mod="$(basename "$d" | tr '-' '_')"
  if ! "$PY" -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('$mod') else 1)" 2>/dev/null; then
    missing=$((missing+1)); echo "  missing from shared venv: $(basename "$d") ($mod)"
    if [ "$APPLY" = "--apply" ]; then
      "$UV" pip install -e "$d" --no-deps --python "$PY" >/dev/null 2>&1 \
        && echo "    -> installed editable" || echo "    -> FAILED (install manually before removing its venv)"
    fi
  fi
done
echo "missing packages: $missing"

if [ "$APPLY" = "--apply" ]; then
  n=0; for v in "$ROOT"/*/.venv "$ROOT"/*/.venv31*; do [ -d "$v" ] && rm -rf "$v" && n=$((n+1)); done
  echo "removed $n redundant per-repo venv dirs"
else
  echo "(dry-run) re-run with --apply to install-missing + remove per-repo venvs"
fi

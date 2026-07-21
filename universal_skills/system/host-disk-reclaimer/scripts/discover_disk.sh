#!/usr/bin/env bash
# Read-only disk discovery. Finds the constrained filesystem and the biggest
# space consumers, then sizes the common reclaimable categories. Deletes NOTHING.
#
# Usage: discover_disk.sh [TARGET_DIR]      (default: largest non-/ mount, else /home)
#
# NOTE: `du` over a multi-hundred-GB tree is slow (minutes). Run this in the
# background or with a generous timeout; the agent should not block on it.
set -uo pipefail
TARGET="${1:-/home}"

echo "## Filesystems (sorted by use%) — find the FULL one"
df -h 2>/dev/null | awk 'NR==1 || ($5+0)>0' | sort -k5 -rh | head -15
echo

echo "## Top-level usage under $TARGET (the elephants)"
du -sh "$TARGET"/* 2>/dev/null | sort -rh | head -20
echo

echo "## Reclaimable package caches"
for d in "$HOME/.cache/uv" "$HOME/.cache/pip" "$HOME/.cache/torch" \
         "$HOME/.cache/pre-commit" "$HOME/.cache/huggingface" "$HOME/.docker"; do
  [ -d "$d" ] && du -sh "$d" 2>/dev/null
done
echo

echo "## Git worktrees (often the #1 hidden consumer)"
for root in "$TARGET/worktrees" "${AGENT_WORKTREE_ROOT:-$TARGET/worktrees}" "$HOME/worktrees"; do
  [ -d "$root" ] && echo "  $root : $(find "$root" -maxdepth 2 -name .git 2>/dev/null | wc -l) worktrees, $(du -sh "$root" 2>/dev/null | cut -f1)"
done
echo

echo "## Virtualenvs (duplicate-per-repo candidates for consolidation)"
find "$TARGET" -maxdepth 5 -type d -name '.venv*' -prune 2>/dev/null | wc -l | sed 's/^/  .venv dirs: /'
echo

echo "## Docker (registry data balloons from accumulated image pushes)"
if command -v docker >/dev/null 2>&1; then
  docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -i registry | sed 's/^/  registry container: /'
  echo "  docker root: $(docker info --format '{{.DockerRootDir}}' 2>/dev/null)"
else
  echo "  (docker CLI not on this host — for a remote host use container-manager-mcp with host=<alias>)"
fi

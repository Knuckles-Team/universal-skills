#!/usr/bin/env bash
# Read-only disk discovery. Finds the constrained filesystem and the biggest
# space consumers, then sizes the common reclaimable categories. Deletes NOTHING.
#
# Usage: discover_disk.sh [TARGET_DIR]      (default: /home)
#
# NOTE: `du` over a multi-hundred-GB tree is slow (minutes). Run this in the
# background or with a generous timeout; the agent should not block on it.
set -uo pipefail
TARGET="${1:-/home}"
BYTE_WARN_PCT="${DISK_BYTE_WARN_PCT:-85}"
INODE_WARN_PCT="${DISK_INODE_WARN_PCT:-80}"
DU_TIMEOUT_SECONDS="${DU_TIMEOUT_SECONDS:-15}"

echo "## Filesystem bytes (warning at ${BYTE_WARN_PCT}%)"
echo "Filesystem Size Used Avail Use% Mounted Status"
df -Ph 2>/dev/null | awk -v warn="$BYTE_WARN_PCT" '
  NR == 1 { next }
  { used=$5; sub(/%/, "", used); status=(used+0 >= warn+0 ? "WARN" : "OK"); print $0, status }
' | sort -k5 -rh | head -20
echo

echo "## Filesystem inodes (warning at ${INODE_WARN_PCT}%)"
echo "Filesystem Inodes IUsed IFree IUse% Mounted Status"
df -Phi 2>/dev/null | awk -v warn="$INODE_WARN_PCT" '
  NR == 1 { next }
  $5 == "-" { print $0, "N/A"; next }
  { used=$5; sub(/%/, "", used); status=(used+0 >= warn+0 ? "WARN" : "OK"); print $0, status }
' | sort -k5 -rh | head -20
echo

echo "## Top-level usage under $TARGET (bounded to ${DU_TIMEOUT_SECONDS}s)"
timeout "$DU_TIMEOUT_SECONDS" du -shx -- "$TARGET"/* 2>/dev/null \
  | sort -rh | head -20
echo

echo "## Reclaimable package caches"
for d in "$HOME/.cache/uv" "$HOME/.cache/pip" "$HOME/.cache/torch" \
         "$HOME/.cache/pre-commit" "$HOME/.cache/huggingface" "$HOME/.docker"; do
  [ -d "$d" ] && timeout "$DU_TIMEOUT_SECONDS" du -shx -- "$d" 2>/dev/null
done
echo

echo "## Git worktrees (often the #1 hidden consumer)"
for root in "$TARGET/worktrees" "${AGENT_WORKTREE_ROOT:-$TARGET/worktrees}" "$HOME/worktrees"; do
  if [ -d "$root" ]; then
    count="$(timeout "$DU_TIMEOUT_SECONDS" find "$root" -maxdepth 2 -name .git 2>/dev/null | wc -l)"
    size="$(timeout "$DU_TIMEOUT_SECONDS" du -shx -- "$root" 2>/dev/null | cut -f1)"
    echo "  $root : $count worktrees, ${size:-measurement timed out}"
  fi
done
echo

echo "## Virtualenvs (duplicate-per-repo candidates for consolidation)"
timeout "$DU_TIMEOUT_SECONDS" find "$TARGET" -xdev -maxdepth 5 -type d -name '.venv*' -prune 2>/dev/null \
  | wc -l | sed 's/^/  .venv dirs (bounded scan): /'
echo

echo "## Docker (registry data balloons from accumulated image pushes)"
if command -v docker >/dev/null 2>&1; then
  docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -i registry | sed 's/^/  registry container: /'
  echo "  docker root: $(docker info --format '{{.DockerRootDir}}' 2>/dev/null)"
else
  echo "  (docker CLI not on this host — for a remote host use container-manager-mcp with host=<alias>)"
fi

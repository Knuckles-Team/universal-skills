#!/usr/bin/env bash
# Garbage-collect a Docker Distribution (registry:2/registry:3) registry to
# reclaim orphaned blobs left by overwritten/untagged image pushes (the classic
# cause of a registry data dir ballooning over time). `-m` also deletes manifests
# that are no longer referenced by any tag.
#
# Requires `storage.delete.enabled: true` in the registry config (registry:3
# default is /etc/distribution/config.yml; registry:2 uses
# /etc/docker/registry/config.yml).
#
# SAFETY: GC is safest with no concurrent pushes. If the registry is actively
# pushed to, put it in read-only maintenance mode first
# (REGISTRY_STORAGE_MAINTENANCE_READONLY_ENABLED=true) and restore after.
#
# Usage: registry_gc.sh [--apply]      (default: dry-run estimate, deletes nothing)
#   For a REMOTE host run the equivalent via container-manager-mcp
#   (cm__container_operations exec_in_container, host=<alias>).
set -uo pipefail
APPLY="${1:-}"

CID=$(docker ps --format '{{.ID}} {{.Image}} {{.Names}}' 2>/dev/null \
        | awk 'tolower($0) ~ /registry/ && tolower($0) !~ /frontend|web/ {print $1; exit}')
[ -z "${CID:-}" ] && { echo "No registry container found on this host."; exit 1; }

CFG=$(docker exec "$CID" sh -c \
  'for f in /etc/distribution/config.yml /etc/docker/registry/config.yml /etc/registry/config.yml; do [ -f "$f" ] && echo "$f" && break; done')
[ -z "${CFG:-}" ] && { echo "Could not locate registry config in container $CID."; exit 1; }
echo "registry container: $CID   config: $CFG"
echo "delete-enabled:"; docker exec "$CID" grep -A2 -i 'delete' "$CFG" 2>/dev/null | sed 's/^/  /'

if [ "$APPLY" = "--apply" ]; then
  echo "## Running garbage-collect -m (real) ..."
  docker exec "$CID" registry garbage-collect -m "$CFG" 2>&1 | tail -3
  echo "Done. Re-measure the registry data dir / df to confirm reclaim."
else
  echo "## DRY-RUN (nothing deleted) — eligible-for-deletion estimate:"
  docker exec "$CID" registry garbage-collect --dry-run -m "$CFG" 2>&1 \
    | grep -iE 'blobs marked|eligible for deletion' | tail -3
  echo "(re-run with --apply to actually reclaim)"
fi

---
name: host-disk-reclaimer
description: Discover what is consuming disk on a host and safely reclaim space. Use when a filesystem is full or nearly full ("no space left on device", df shows 90%+), when /home or / is ballooning, or when the user asks to free up space, clean caches, prune stale git worktrees, garbage-collect a Docker registry, or consolidate per-repo virtualenvs. Runs read-only discovery (df + du breakdown) first, then gated reclamation in safety order: regenerable caches, merged+clean git worktrees, Docker registry GC, docker system prune, and redundant venv consolidation — always preserving in-flight work, live service data, and application databases. Works on the local host or, for a remote host, via tunnel-manager (SSH) and container-manager-mcp (Docker over SSH). Do NOT use to delete application data, dump databases, or migrate/rotate live services to other hosts (that is a deployment-planner + tunnel-manager job).
license: MIT
tags: [system, disk, cleanup, docker, registry, git-worktree, cache, venv, ops]
metadata:
  author: Knuckles-Team
  version: '0.1.21'
---

# Host Disk Reclaimer

Free space on a host by **discovering** the biggest consumers, then **reclaiming**
only what is safe — never touching in-flight work, live service data, or databases.

All scripts live in `scripts/` and default to **dry-run / read-only**; destructive
steps require an explicit `--apply`. Make them executable once: `chmod +x scripts/*`.

## Golden rules
- **Discover before deleting.** Always run discovery first and let the sizes drive priorities.
- **Reclaim regenerable things only.** Caches, merged worktrees, orphaned registry blobs, duplicate venvs — all rebuildable. Never delete source, databases, or a service's bind-mounted data.
- **Preserve in-flight work.** A git worktree is removed only if it is BOTH clean AND merged. Dirty/unmerged = keep.
- **Measure each step.** Capture `df -h <fs>` before/after so reclaimed space is reported, not guessed.
- **`du` is slow** on big trees (minutes) — run discovery/measurement in the background; do not block on it.

## Step 1 — Discover (read-only)
Run `scripts/discover_disk.sh [TARGET_DIR]`. It reports: the fullest filesystem,
the top-level `du` breakdown of the target, the size of package caches, the git
worktree count/size, the number of `.venv` dirs, and the Docker registry container.
Identify which category dominates — that is where to focus.

Typical ranking on a dev/homelab host: **git worktrees > docker registry > workspace venvs > package caches**.

## Step 2 — Reclaim, safest first
Run each step's script in **dry-run** to preview, then re-run with `--apply`.
Record `df -h` before/after each.

1. **Package & tool caches** (safest) — `scripts/clear_caches.sh [REPO_ROOT]`.
   Clears `uv`/`pip`/`torch`/`pre-commit` caches and (if REPO_ROOT given) per-repo
   `__pycache__`/`.mypy_cache`/`.ruff_cache`/`.pytest_cache`/`.hypothesis`.
2. **Stale git worktrees** (usually the biggest win) —
   `scripts/prune_worktrees.py <worktrees-root>` (dry-run) → review the KEEP list →
   `--apply`. Removes only clean+merged worktrees via `git worktree remove` and
   deletes their merged branches; keeps everything dirty or unmerged.
3. **Docker registry GC** — `scripts/registry_gc.sh` (dry-run shows eligible blobs)
   → `--apply`. Reclaims orphaned blobs from overwritten/untagged image pushes.
   Needs `delete.enabled: true`; safest with no concurrent pushes.
4. **Docker system prune** — remove unused images/containers/volumes/build cache.
   On a SHARED swarm host be conservative: prefer `docker buildx prune -f` (build
   cache only) and `docker image prune -f` (dangling only) over a full
   `docker system prune --all --volumes`, which can evict images other nodes pull.
   Note: Docker's data-root is usually on `/`, not `/home` — confirm with
   `docker info` before assuming a prune helps the full filesystem.
5. **Consolidate virtualenvs** — `scripts/consolidate_venvs.sh <SHARED_VENV> <PACKAGES_ROOT>`
   (dry-run lists packages missing from the shared venv) → `--apply` installs those
   editable (`--no-deps`) then removes the redundant per-repo `.venv` dirs. Verify
   the shared venv imports every package (0 missing) before relying on it.

## Step 3 — Report & recommend
Summarize total reclaimed (sum of before/after `df` deltas) and the new headroom.
For heavy **live service data** seen in discovery (e.g. media, registry, DB volumes,
Prometheus TSDB) that cannot be deleted, do NOT move it here — recommend rotating
the service to a host with capacity using the `deployment-planner` skill (pick the
target by free capacity) and `tunnel-manager` (rsync the bind-mount + redeploy the
stack). Surface it as a proposal for the user to approve.

## Remote hosts
This skill is host-agnostic. To reclaim space on a REMOTE machine:
- Discovery / cache / worktree / venv steps: run the scripts over SSH via
  `tunnel-manager` (the inventory alias resolves to `ssh://user@host:port`), or use
  `host-resource-sampler` for the df/utilization snapshot.
- Docker steps: use `container-manager-mcp` (`cm__container_operations` →
  `exec_in_container` / `prune_containers`, `cm__image_operations`,
  `cm__volume_operations`, `cm__system_operations` → `prune_system`) with
  `host=<alias>` to target that machine's Docker over SSH — no need to copy scripts.

## Known gotchas (from real runs)
- A separate `/home` partition can be 100% full while `/` has hundreds of GB free — always check **which** filesystem is constrained; a host `docker system prune` frees `/var/lib/docker` (usually on `/`), not `/home`.
- Clearing the `pre-commit` cache makes the next `pre-commit`/commit slow (it reinstalls hook envs) — expect a one-time delay.
- registry:3 config is `/etc/distribution/config.yml` (registry:2 used `/etc/docker/registry/config.yml`) — the GC script auto-detects.
- Deleting per-repo `.venv`s only affects local dev/test; running services use container venvs, not these.

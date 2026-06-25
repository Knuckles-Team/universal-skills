#!/usr/bin/env python3
"""Audit git worktrees under a root and prune the ones that are safe to remove.

A worktree is SAFE to remove only when BOTH hold:
  (a) clean  — no uncommitted changes (`git status --porcelain` empty), AND
  (b) merged — its HEAD is an ancestor of the repo's main/master (local OR
      origin), i.e. all of its commits are already in the mainline.
Dirty or unmerged worktrees are in-flight work and are KEPT, never touched.

Removal uses `git worktree remove --force` (updates the repo's worktree admin)
and deletes the now-merged branch.

Usage:
  prune_worktrees.py <worktrees-root> [--apply]
      default is a DRY-RUN that only classifies; pass --apply to remove.
  Layout assumed: <worktrees-root>/<repo>/<branch>/...
"""
import os
import subprocess
import sys


def git(args, cwd):
    return subprocess.run(
        ["git", "-C", cwd, *args], capture_output=True, text=True
    )


def classify(wt):
    dirty = bool(git(["status", "--porcelain"], wt).stdout.strip())
    head = git(["rev-parse", "HEAD"], wt).stdout.strip()
    merged = any(
        git(["merge-base", "--is-ancestor", head, base], wt).returncode == 0
        for base in ("main", "master", "origin/main", "origin/master")
    )
    return dirty, merged


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: prune_worktrees.py <worktrees-root> [--apply]")
        sys.exit(2)
    root = args[0]
    apply = "--apply" in args[1:]

    prune, keep = [], []
    for repo in sorted(os.listdir(root)):
        rp = os.path.join(root, repo)
        if not os.path.isdir(rp):
            continue
        for branch in sorted(os.listdir(rp)):
            wt = os.path.join(rp, branch)
            if not os.path.exists(os.path.join(wt, ".git")):
                continue
            dirty, merged = classify(wt)
            if not dirty and merged:
                prune.append(wt)
            else:
                keep.append((wt, "dirty" if dirty else "unmerged"))

    print(f"PRUNE (clean + merged): {len(prune)}")
    print(f"KEEP  (in-flight):      {len(keep)}")
    for wt, why in keep:
        print(f"  KEEP {wt}  [{why}]")
    if not apply:
        print("\n(dry-run) re-run with --apply to remove the PRUNE set")
        return

    removed = 0
    for wt in prune:
        common = git(
            ["rev-parse", "--path-format=absolute", "--git-common-dir"], wt
        ).stdout.strip()
        repo = common[:-5] if common.endswith("/.git") else os.path.dirname(common)
        branch = git(["rev-parse", "--abbrev-ref", "HEAD"], wt).stdout.strip()
        if git(["worktree", "remove", "--force", wt], repo).returncode == 0:
            git(["branch", "-D", branch], repo)
            removed += 1
        else:
            print(f"  FAILED to remove {wt}")
    print(f"\nremoved {removed}/{len(prune)} worktrees")


if __name__ == "__main__":
    main()

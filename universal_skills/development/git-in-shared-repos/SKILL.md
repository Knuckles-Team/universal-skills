---
name: git-in-shared-repos
domain: development
skill_type: skill
description: >-
  Git operations that are safe in a personal checkout but corrupt or leak work
  in a repository shared by multiple concurrent worktrees or sessions —
  harness-managed worktree isolation, git stash, and git add -A/-.  Use
  before running any of those three, or before touching a checkout you did
  not create yourself, in any repository with more than one active worktree.
license: MIT
tags: [git, worktree, shared-repository, hygiene]
metadata:
  version: '1.0.0'
---

# Git in shared, multi-worktree repositories

Most repositories in this fleet are worked on from several linked worktrees
at once — one per branch, lane, or session — all sharing a single Git
repository (`$GIT_COMMON_DIR`, the `.git` directory the primary checkout and
every `git worktree add` sibling point back to). Three ordinary-looking git
operations are unsafe there, and all three fail the same way: each keeps its
state in that one shared location instead of per-worktree, so an operation
that looks locally scoped actually mutates something every other worktree or
session sees. Before running any of the three below, or editing a checkout
you did not create, run `git worktree list` and assume any other linked
worktree may have a concurrent session using it right now.

## Never use harness-managed automatic worktree isolation

An agent harness's own "give me an isolated worktree" tool can write
`core.bare = true` into the **shared** `$GIT_COMMON_DIR/config` when it stands
up the isolated worktree, and never restores it afterward. Once that happens,
every other linked worktree of that same repository — not just the one the
tool touched — sees the checkout as bare: `git status`, `git commit`, and
anything that calls `git rev-parse --show-toplevel` fails with `fatal: this
operation must be run in a work tree`, invisibly, for every concurrent
session, until someone notices and runs `git config core.bare false` to
repair it.

Use a real worktree instead, created with the ordinary plumbing:

```
git worktree add <path> -b <branch> <base>
```

This is per-worktree state from the start; nothing it does touches the
shared config.

## Never `git stash` in a shared repository

`refs/stash` is a single, repository-wide ref kept in `$GIT_COMMON_DIR` — it
is **not** per-worktree. If two worktrees of the same repository each stash
at different times, they are pushing onto one shared stack. A `git stash
pop` in one worktree restores whatever is on top of that stack, which may be
a **different worktree's or session's uncommitted work**. The pop succeeds;
it does not error or warn — it just hands you someone else's diff and
consumes their stash entry, which can look like lost work until someone
reconstructs it (recoverable, if at all, only through `git fsck
--unreachable` and reapplying by blob SHA).

To compare against or temporarily set aside work without touching shared
state, use one of:

```
git diff <base> -- <path>                 # see what changed, no stash needed
git show <base>:<path>                    # read another revision's content
git worktree add --detach <tmp> <base>    # a throwaway clean tree to compare against
git checkout -- <path>                    # discard local edits, scoped to paths you own
```

## Never stage with `git add -A` or `git add .`

A shared worktree routinely contains more than your own change: another
lane's in-progress edits, scratch files, logs, caches, handoff notes, or
build output that happens to sit in the tree. A blanket `add` does not
distinguish any of that from the change you meant to commit — it stages
everything under the given path, silently folding unrelated or sensitive
content into your commit.

Stage an explicit, reviewed allowlist instead:

```
git add -- path/to/file ...
git add -u -- exact/path ...     # for deletions
```

Then, before every commit, re-read what is actually about to be committed —
`git diff --cached --name-status` for the file list, `git diff --cached` for
the content — rather than trusting what you intended to stage.

## The common thread

All three failures are the same shape: a git feature whose state lives in
the repository-wide common directory rather than in the worktree you are
sitting in. `core.bare` is one config file shared by every linked worktree;
`refs/stash` is one ref shared by every linked worktree; a blanket `add`
reads whatever happens to be sitting in your particular worktree, which in a
shared repository is never guaranteed to be only your own work. Treat any
git operation whose effect you cannot name as "only this worktree, only this
commit" as suspect until you have checked where its state actually lives.

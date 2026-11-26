## 8. Build and test operating rules

### Running the suite

```bash
export CARGO_INCREMENTAL=0
cargo check -p medulla-types                          # fastest inner loop
cargo check -p medulla-engine                   # full closure
cargo test -p medulla-engine --lib -j 8 -- --test-threads=4
```

- **Do NOT export `CARGO_TARGET_DIR`.** The committed `.cargo/config.toml` already sets
  `[build] target-dir = "target-isolated"`. That path is *relative*, so it resolves
  against each worktree root — every worktree gets its own isolated target dir with no
  env var and no action after checkout. An exported `CARGO_TARGET_DIR` overrides it
  (cargo's own precedence) and **`lane-guard` refuses the commit** unless the export
  points at exactly this lane's partitioned dir
  (`meristem/scripts/check_lane_guard.py`, `_check_cargo_target_override`).
- **NEVER omit `--test-threads=4`. The suite deadlocks at the 24-thread default.**
- **`-j` bounds the COMPILER, not the harness.** `-j 8` limits `rustc` jobs;
  `--test-threads` after `--` limits the test harness. They are different knobs
  and you need both.
- Cargo ignores `CPUQuota`; `-j` is the only lever. 3-4 concurrent cargo lanes on
  this workspace is the practical ceiling.
- Full gate before claiming done: `pre-commit run --all-files`, no `--no-verify`
  — but **not bare in a shared checkout**, because it stashes and can drop your
  unstaged work (**G11**); run it from a throwaway detached worktree with a
  lane-private `PRE_COMMIT_HOME` and `TMPDIR`, as *Git, in a shared
  multi-worktree repo* below already requires.
  Plus `bash scripts/constrained_parallelism_gate.sh` (GOC-70), which re-runs the
  lib suite and the concurrency-sensitive integration binaries under `taskset -c 0,1`.

### Git, in a shared multi-worktree repo

- **NEVER `git stash`.** `refs/stash` lives in `$GIT_COMMON_DIR` and is repo-wide
  across 50+ worktrees; a `pop` in one lane silently takes another lane's WIP. To
  compare against clean main use `git diff main -- <path>`, `git show main:<path>`,
  or `git worktree add --detach <tmp> main`.
- **NEVER `git add -A` or `git add .`.** Stage an explicit reviewed allowlist:
  `git add -- path/to/file ...`. Re-read `git diff --cached` before committing.
  Handoff notes, baselines, logs, caches and scratch files are never product artifacts.
- **NEVER use the harness's worktree-isolation tool** on this repo — it writes
  `core.bare = true` into the shared config and breaks every linked worktree. Use
  a real `git worktree add "$WORKTREE_ROOT/<repo>/<branch>" -b <branch>` (or
  `rm_worktree add`). Each session takes a distinct branch.
- Do not edit the repository-manager-owned canonical checkout; its background sync
  resets the working tree.
- Run gates in a throwaway detached worktree when a formatting hook could rewrite
  a shared checkout, with a lane-private `PRE_COMMIT_HOME` and `TMPDIR`.


**Disk budgeting, the Rust idioms this workspace has already paid for
(bind-before-yield / E0597, crates.io-only, `bump-my-version` and never a
hand-edited version string, loud feature-gating), and the reporting rules that
govern how a number leaves your hands (no ratchets, the permitted reviewed-ledger
shape, report the real number with its command and its composition) are in
[`references/build-and-test-reference.md`](references/build-and-test-reference.md).
Read the disk section before starting a long build and the reporting section
before publishing a count.**

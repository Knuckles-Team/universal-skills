# Epistemic-graph build and test reference

Deep reference for `epistemic-graph-development`: the disk budget a build in
this workspace actually needs and why worktree *placement* is the lever, the
Rust idioms this workspace has already paid for once, and the reporting rules
that govern how a number leaves your hands. The parent
[`SKILL.md`](../SKILL.md) §8 keeps the commands you run every loop — the suite
invocation with its mandatory test-threads bound (`--test-threads=4`), and the
`Git, in a shared multi-worktree repo` prohibitions that **G11** indexes. Open
this file before you start a long build, before you return a borrowed redb
guard, and before you publish a count.

### Disk

**Budget disk before you start a build; check free space with `df -h` first.** One EG
target directory runs tens of gigabytes and a full multi-feature target has reached
~97 GiB, so several concurrent lanes can fill a filesystem mid-build — which corrupts
results rather than failing cleanly.

Because `target-dir` is relative, each worktree's target lives **beside that worktree**.
Keeping the build off a constrained filesystem is therefore a *worktree-placement*
decision — put the worktree on a roomy volume — not a `CARGO_TARGET_DIR` export (see
above: exporting one is refused by `lane-guard`). Do not point build or test temp at a
`tmpfs` mount; on a typical Linux host `/tmp` is RAM-backed and bulk test temp there
consumes memory. Prefer a disk-backed `TMPDIR`.

### Rust idioms this workspace has already paid for

- **Bind before yielding.** In `eg-mutation-store`, a block's or function's tail
  expression outlives the local it borrows, so returning a redb `AccessGuard` or a
  `list_tables` iterator directly fails borrowck with **E0597**. Bind to a local,
  then return it. The comment appears **twice**, both in
  `crates/eg-mutation-store/src/store/identity.rs` (`:314` and `:573`) — none in
  `store/ledger.rs`. (`src/raft/tests.rs:2081`/`:2132` cite E0597 for an unrelated
  shape in a different crate.)
- **crates.io only.** No `git = ` source; no `path = ` outside the workspace.
- **Never hand-edit a version string** — `bump-my-version bump {patch|minor|major}`
  only, and every version-bearing file must be registered in `.bumpversion.cfg`.
  Re-lock (`uv lock`) in the same change as any Python dependency edit.
- **Feature-gated code must fail loudly, never vacuously.** A gated-out `Method`
  keeps its enum variant and falls to the explicit "not built" catch-all.

### Reporting rules

- **No ratchets** (**G8**). A *self-updating* baseline — anything with an
  `--update-baseline` flag — is forbidden outright, and none exists in this repo.
  What IS permitted, and what `.repo-layout.toml`, `tests/integration_failure_baseline.txt`
  and `tests/protocol_unbound_baseline.txt` all are, is a **reviewed human ledger**:
  it hides no finding, every entry carries an owner and a reason, it grows only by a
  deliberate edit, and it FAILS when an entry rots — when something new joins it and
  when something on it starts passing. Copy that shape or add nothing.
- Report the real number with the command that produced it (**G1**), and its
  composition, not just its size (**G10**).
- The gate suite being red does not license adding to it — keep a per-hook
  **census** (not a frozen file) so a composition's own regressions stay visible.

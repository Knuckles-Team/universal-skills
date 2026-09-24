# Traps reference — `graphos-ecosystem-development`

Each trap below cost real time in this ecosystem. The left column is what you see; the
right column is what is actually happening and what to do instead.

## Git and worktrees (shared multi-worktree repositories)

| Symptom / temptation | Reality | Do instead |
|---|---|---|
| `fatal: this operation must be run in a work tree` in every worktree | Harness worktree isolation wrote `core.bare=true` into the shared config | Never use it; `git config core.bare false` repairs; use `git worktree add` |
| `git stash pop` "worked" | `refs/stash` is repo-wide; you may have consumed another lane's WIP | `git show HEAD:<path>`, `git diff main -- <path>`, a `wip:` commit, or `git stash create` (writes no ref) |
| Unexpected modified files in "your" worktree | Another lane is working there | Stop and report; never checkout/restore/reset/clean them |
| `git branch --merged` lists a branch as merged | Its worktree may still hold the only copy of uncommitted work | Ancestor check + clean-worktree check before pruning |
| `update-ref` advanced the branch | The worktree and index did not move; the next commit silently reverts everything in between | `merge --ff-only`; verify by tree |
| "Index wiped" | The worktree files are usually intact | `git reset --mixed` recovers; never `--hard` |
| Two lanes' commits landed under each other's subjects | Both wrote the same `/tmp/msg.txt` | Lane-unique message paths |
| pre-commit run overlapped your edits and `git status` is clean | pre-commit stashed and restored the unstaged tree | Never edit while a long hook run is in flight; re-verify each change by content |
| Edited the canonical checkout | A repository-manager sync resets it | Always a worktree |

## Builds and environments

| Symptom | Reality | Do instead |
|---|---|---|
| "no variant named X" for code that clearly defines X | Shared/corrupted cargo target from an exported `CARGO_TARGET_DIR` | Unset it; each worktree has `target-isolated` |
| Load 60+ on a 24-core host | Several cargo lanes; cargo ignores CPU quotas | Budget by cargo lanes (3–4 per host, `-j`); build hosts only |
| Whole tmux session killed | systemd-oomd kills the scope | Heavy work in transient units / build hosts |
| Test run filled RAM | `/tmp` is tmpfs | Temp under a lane directory on disk |
| Phantom AU failures citing the project's own guards | `uv run pytest` used the system interpreter, or a test's `uv sync` rebuilt the lane venv | `scripts/uv_workspace.py run --all-extras -- pytest`; print `sys.executable`; believe a `venv-package-count` alarm |
| pytest exited 75 mid-run | A guard `realpath()`-ed the uv interpreter and `execve`'d away | Never realpath a venv interpreter |
| AU suite hangs; `--timeout` never fires | Blocked in an anyio worker thread on a live engine call | `py-spy dump`; make the test hermetic |
| AU tests fail against engine features that exist | The EG fast path served a stale prebuilt wheel | Compare wheel version to `Cargo.toml`; `EPISTEMIC_GRAPH_SOURCE_BUILD=1` |
| A long commit "succeeded" per `systemctl show` | `--collect` reaped the unit; status is the default | Judge by state: did HEAD move, is the index empty |
| A hook fails only in a worktree | Discovery walked up from `$PWD` for the fleet root | Check the gate's path discovery before the code |

## Gates and measurement

| Symptom | Reality | Do instead |
|---|---|---|
| Gate green | It may have scanned nothing, crashed quietly, or never run | Prove it fails on a known-bad input |
| mypy count 19 vs hook count 5 | The hook runs a different universe (excludes, deps) | Scope work from the hook's output |
| Gate helper sees an empty repo inside a hook | Git exports `GIT_DIR`/`GIT_INDEX_FILE` into hooks | Test both ways; use the shared git-scan helper |
| Refactor made a gate red with no behaviour change | Gate keyed on a symbol name, byte offset or line number | Key on content/behaviour; follow the call graph |
| Extracted helper is a "100% duplicate" | Extraction turned a literal into a clone | Remove the repetition (table), don't disguise it |
| Extraction broke a warning's source line | `stacklevel` counts frames; a comprehension is a frame | Verify attribution empirically |
| mypy red after a pure extraction | A narrowing no longer crosses the new boundary | Restructure, or keep the expression inline — never `cast`/ignore |
| Complexity improved, code got worse | The metric measured 2 of 5 properties | Also watch file length, helper names, arity |
| `pre-commit run --files` passed | It skips `always_run` hooks | Not evidence of a full pass |
| Push "passed" with no hooks | The pre-push shim still points at an old config path | Reinstall hooks after moving a config |
| Every commit red on `check-release-catalogs` | A half-registered connector or a hand-edited generated manifest | Register at every site; regenerate, never hand-edit |
| Digest/golden test red after a rename | A serde-tagged rename changed the wire bytes | Recompute goldens in the same commit; re-run tests last |
| "Pre-existing" failure | Maybe, maybe not | Judge differentially vs the base ref at node-id granularity; fix what you hit |

## Services and probes

| Symptom | Reality | Do instead |
|---|---|---|
| Service probe green, users cannot sign in | Service token path ≠ browser path | Probe the browser path and the admission call it triggers |
| An identity lost its roles | `RegisterIdentity` replaces the whole role set | Always send the full role set |
| Delegation "cannot find" a skill that exists | It ingested as a `WorkflowDefinition`, not `CallableResource(AGENT_SKILL)` | `skill_type: skill` in the frontmatter |
| A control was deployed and changed nothing | It was wired at one entrypoint; others bypass it | Wire at the chokepoint |

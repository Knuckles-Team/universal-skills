# "Already addressed?" — triage + deep-verify decision table

Two-pass classification. **Pass 1** is a cheap heuristic that buckets every open item.
**Pass 2** is a deep, per-item investigation that is run only on the items Pass 1 marks
as *maybe addressed*, to confirm a fix actually landed before recommending a close.

## Pass 1 — heuristic triage (cheap, from list/search data)

### Issues
| Signal | Bucket | Status |
|---|---|---|
| Has a **linked open PR** (or `linked_pull_requests`, or a PR whose body says `fixes #N`) | in progress | `in-progress` |
| Has a **merged/closed PR** referencing it, but the issue is still open | maybe addressed → Pass 2 | (`addressed` if confirmed) |
| Referenced by a recent **commit** on the default branch | maybe addressed → Pass 2 | (`addressed` if confirmed) |
| Last activity is **stale** and no linked work | needs plan | `needs-action` |
| Fresh, no linked work | needs plan | `needs-action` |

### Pull requests
| Signal | Status | Notes |
|---|---|---|
| Open, `draft: true` | `in-progress` | Recommend: finish + mark ready. |
| Open, `mergeable_state: clean`, approved | `needs-action` | Recommend: merge. |
| Open, failing checks / `mergeable_state: dirty`/`blocked` | `needs-action` | Recommend: fix CI or rebase (cross-link the CI sweep skill). |
| Open, awaiting review | `needs-action` | Recommend: request/perform review. |
| Open, conflicts with base | `needs-action` | Recommend: rebase/resolve. |

## Pass 2 — deep verification (only for "maybe addressed")

For each candidate, gather enough evidence to either confirm `addressed` (safe to close)
or downgrade to `needs-action`:

1. `gith__issues action=get {owner, repo, number}` — read body + timeline; collect every
   referenced PR number and commit SHA (look for `fixes/closes/resolves #N`, cross-refs).
2. For each referenced PR: `gith__pulls action=get {owner, repo, number}` — confirm
   `merged: true` and which files it touched (`changed_files`, or list the PR's files).
3. Open the **referencing commit / changed file** to verify the fix is real, not a no-op:
   - `gith__commits action=get {owner, repo, sha}` for the diff, and/or
   - `gith__contents action=get {owner, repo, path, ref}` to read the current source on the
     default branch and confirm the described change is present.
4. Verdict:
   - Fix present on default branch + PR merged → `status: addressed`,
     `evidence: "merged PR #N landed <change> in <file>"`, `recommendation: "Close #M"`.
   - Referenced work reverted, or change absent, or PR closed-unmerged → `status: needs-action`,
     `evidence: "PR #N closed without merging / change not on main"`.

## For items that still need a plan

Read the relevant source (`gith__contents`) around the reported problem to write a
**one-line root-cause note** and a **concrete recommended next step** (the `recommendation`
field). Keep it actionable: name the file/function and the change, not "investigate".

## Priority assignment
- `high` (P1): PRs ready to merge, regressions/bugs blocking users, failing CI on default branch.
- `medium` (P2): normal bugs, enhancements with a clear path.
- `low` (P3): nice-to-have enhancements, stale/low-signal items.

## Output contract
Emit one normalized JSON object per item (see `scripts/build_plan.py` docstring for the schema)
and pipe the list through `build_plan.py` to render the final Markdown plan.

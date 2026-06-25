# `gith__pulls` / `gith__actions` cheatsheet (github-mcp)

Read just-in-time when driving the sweep. All calls go through the multiplexer's
`gith__*` tools (the GitHub MCP holds its own auth — no `gh` CLI / `GITHUB_*` token).

## `gith__pulls` — `action` + `params_json`
| action | params_json | returns |
|--------|-------------|---------|
| `list` | `{"owner","repo","state":"open","per_page":100,"max_pages":0}` | open PRs for a repo (basic objects: number, title, user, draft, base/head, created_at, comments) |
| `get`  | `{"owner","repo","pull_number"}` | full PR: `mergeable`, `mergeable_state` (`clean`/`dirty`/`blocked`/`behind`/`unstable`), `additions`, `deletions`, `changed_files`, `review_comments` |
| `update` | `{"owner","repo","pull_number", ...}` | mutate (title/body/base/state) — opt-in only |
| `create` | `{"owner","repo","title","head","base", ...}` | open a PR — not used by this sweep |

Notes:
- `list` does NOT include `mergeable_state` or check status — fetch those with `get` (and `gith__actions`) per PR in the diagnose step.
- `max_pages: 0` pages through everything; results are large and the harness spills them to a file — feed that file to `scripts/summarize_prs.py`, do not read it raw.

## Checks for a PR's head
- `gith__actions action=list_runs {"owner","repo","branch":"<pr.head.ref>","per_page":10}` → latest runs on the PR branch; conclusion `success`/`failure`/… is the checks signal.
- (`head.ref` comes from the PR object; for forks the branch lives under the fork — fall back to the run whose `head_sha` matches the PR head SHA.)

## Repo enumeration
- User account: `gith__repos action=list` → keep repos whose `owner.login` == the user.
- Org account: `gith__orgs action=repos {"org":"<login>"}` (or `gith__repos` org variant).
- Record `default_branch`; skip `archived`/`disabled` repos.

## Mergeable-state → verdict mapping
| `mergeable_state` | meaning | verdict |
|-------------------|---------|---------|
| `clean` | mergeable, checks green, approved/!required | ✅ ready to merge |
| `unstable` | mergeable but a non-required check is failing/pending | ⚠️ checks failing/pending |
| `blocked` | required review or status not satisfied | ⏳ needs review / required check |
| `dirty` | merge conflict | ❌ conflicts — rebase needed |
| `behind` | base moved; needs update | 🔄 update branch |
| `draft` (PR.draft=true) | work in progress | 📝 draft |

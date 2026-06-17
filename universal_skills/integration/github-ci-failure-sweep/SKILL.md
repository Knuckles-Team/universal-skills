---
name: github-ci-failure-sweep
description: >-
  Sweeps GitHub Actions across one or more GitHub accounts (a user and/or an
  organization, all repositories) and reports which CI pipelines are currently
  failing, with the failing workflow, last failed run, and a probable cause. Use
  when asked which CI/pipelines are red, to audit Actions health across repos, to
  find failing builds for a user/org, or to triage broken CI before fixing it.
  Defaults to read-only analysis; re-running or cancelling runs is opt-in and runs
  only on explicit confirmation. Do NOT use for inspecting a single PR's checks
  (use github-tools) or for GitLab pipelines.
license: MIT
tags: [github, ci, actions, pipelines, workflows, ops]
metadata:
  author: Genius
  version: '0.47.0'
---

# GitHub CI Failure Sweep

## Overview

Cross-account GitHub Actions health check. Enumerates every repo under the target
accounts (e.g. the `Knucklessg1` user **and** the `Knuckles-Team` org), finds the
**latest failing run per workflow**, and emits a compact Markdown report grouped by
repo, with a probable cause per failure. Read-only by default; re-runs are opt-in.

Drives the **GitHub MCP server** (`github-mcp`, prefix `gith__`). No `gh` CLI or
local `GITHUB_*` token is required — the MCP server holds its own auth.

## Tool discovery (dynamic MCP fleet)

1. `find_tools("github actions workflow runs CI")`.
2. `load_tools(tools=["gith__actions","gith__repos","gith__orgs"])`.

`gith__actions` takes `action` + `params_json`; actions are
`list_workflows|list_runs|get_run|trigger_dispatch|rerun|cancel|delete_run`.
See `references/actions-tool-cheatsheet.md`.

## Inputs
- **accounts**: `[{login, type}]`. Default:
  `[{login: "Knucklessg1", type: "user"}, {login: "Knuckles-Team", type: "org"}]`.
- **branch_scope**: `default` (only each repo's default branch — recommended) or `all`.

## Workflow

### Step 1 — Discover repositories
- User: `gith__repos action=list`; keep repos owned by the login.
- Org: `gith__orgs action=repos {"org": "<login>"}`.
- Record `default_branch`; skip archived/disabled repos.

### Step 2 — Fetch failing runs per repo (filtered)
For each repo, call `gith__actions action=list_runs` filtered **server-side** to keep the
payload small:

```json
{"owner": "<login>", "repo": "<repo>", "status": "failure", "per_page": 15}
```

Add `"branch": "<default_branch>"` when `branch_scope=default`. The result is large and
will likely be spilled to a file by the harness — **do not read it raw**.

### Step 3 — Reduce to the latest failing pipeline per workflow
Feed each repo's result (file path or piped JSON) through the reducer, which keeps only the
latest run per `(repo, workflow, branch)` and only failing conclusions
(`failure|timed_out|cancelled|action_required|startup_failure`):

```bash
# one or many repo dumps at once
python scripts/summarize_runs.py repo1_runs.json repo2_runs.json --format json   # compact list
python scripts/summarize_runs.py repo1_runs.json --format md                      # report table
```

If every repo is green, the reducer reports "✅ No failing pipelines detected."

### Step 4 — Diagnose each failure
For each failing run in the reduced list, `gith__actions action=get_run
{"owner","repo","run_id"}` and read the failing job/step to add a one-line probable cause
(e.g. "ruff lint failed", "pytest: 3 failures", "docker build timed out"). Cross-link the
`github-backlog-planner` skill if a failure is blocking an open PR.

### Step 5 — Present the report
Render the Markdown table (Step 3 `--format md`) augmented with the probable-cause notes
and a suggested fix per pipeline. Group by account → repo.

### Step 6 — Opt-in remediation (only on explicit confirmation)
Never trigger reruns without the user confirming. When asked:
- Re-run failed jobs: `gith__actions action=rerun {"owner","repo","run_id"}`.
- Cancel a stuck run: `gith__actions action=cancel {"owner","repo","run_id"}`.

## Related skills
- `github-backlog-planner` — full issue/PR backlog sweep + plan.
- `github-tools` — single-PR check inspection (do not duplicate here).

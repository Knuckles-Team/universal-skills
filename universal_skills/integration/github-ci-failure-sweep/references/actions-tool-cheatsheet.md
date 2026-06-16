# `gith__actions` cheatsheet (GitHub MCP)

`gith__actions` takes `action` + a `params_json` string. Actions:
`list_workflows | list_runs | get_run | trigger_dispatch | rerun | cancel | delete_run`.

## Listing runs without blowing the token budget

`list_runs` returns full run objects (~13KB each). A naive call across many repos will
exceed the tool-output limit and spill to a file. Reduce the payload three ways:

1. **Filter server-side.** GitHub's runs endpoint accepts query params — pass them in
   `params_json`:
   - `"status": "failure"` — only failed runs (also: `cancelled`, `timed_out`, `action_required`).
   - `"branch": "<default_branch>"` — restrict to the branch CI gates on.
   - `"per_page": 10` — cap results.
   Example:
   ```json
   {"owner": "Knuckles-Team", "repo": "geniusbot", "status": "failure", "per_page": 10}
   ```
2. **Per-workflow latest.** Even filtered, you want the *latest* run per workflow, not the
   whole history. `scripts/summarize_runs.py` does this dedup.
3. **Never read the spilled file raw.** When the harness saves the result to a file, feed
   that file straight into the reducer:
   ```bash
   python scripts/summarize_runs.py /path/to/spilled_list_runs.json --format md
   ```

## Run object fields used

| Field | Use |
|---|---|
| `repository.full_name` | group by repo |
| `workflow_id`, `path`, `name` | identify the pipeline (`path` is cleanest; `name` may have a `#1234` suffix) |
| `head_branch` | branch the run was on |
| `status` | `completed` vs in-progress (only `completed` has a final result) |
| `conclusion` | `success` / `failure` / `timed_out` / `cancelled` / ... |
| `updated_at` | pick the latest run per workflow |
| `html_url`, `id`, `run_number`, `head_sha` | link + reference the run |

## Diagnosing a failure

For each failing run, `gith__actions action=get_run {"owner","repo","run_id"}` returns the
run detail. Read the failing job/step to write a one-line probable cause (e.g. "ruff
lint failed", "pytest 3 failures", "docker build timeout"). If deeper logs are needed and a
local `gh` CLI happens to be available, `gh run view <id> --repo o/r --log-failed` is handy —
but do not assume `gh` exists; the MCP path is canonical here.

## Opt-in remediation (confirm first)
- Re-run failed jobs: `gith__actions action=rerun {"owner","repo","run_id"}` (some servers
  expose a `failed_only` flag — re-running only failed jobs is preferred).
- Cancel a stuck run: `gith__actions action=cancel {"owner","repo","run_id"}`.

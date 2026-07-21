---
name: dependency-modernizer
domain: development
skill_type: skill
description: >-
  Bump every PyPI-resolvable dependency in one or many repos' pyproject.toml
  files to its newest version on PyPI, preserving comments and formatting via
  a tomlkit round-trip edit, while safely leaving workspace/intra-repo
  members, CVE-pinned security floors, and complex (direct-URL/VCS or
  marker-qualified) specs untouched. Use when the user asks to modernize,
  refresh, or bump dependencies to the latest version across one repository
  or a whole fleet of repositories.
license: MIT
tags: [dependencies, pyproject, pypi, modernization, fleet, tomlkit]
metadata:
  version: '1.2.1'
  author: Genius
---

# Dependency Modernizer

Resolve every dependency in one or many `pyproject.toml` files to its newest
version on PyPI and rewrite the specifier to `>=<latest>`, dropping any upper
bound unless told to keep it. Editing goes through `tomlkit`, so every byte
outside the changed specifiers — comments, quoting, indentation, key order —
survives the round trip. `[project].version` and `[build-system]` are never
touched.

## Two-phase caveat

This skill only performs the bump. It does **not** run `uv lock` /
`pip-compile` or a test suite. After bumping, reconcile each touched repo
separately: regenerate its lockfile (`uv lock`) and run its test suite to
catch anything the new versions break. Treat the bump and the reconciliation
as two independent steps, never one.

## What gets skipped (and why)

For every `[project].dependencies` entry and every list under
`[project.optional-dependencies]`, an entry is left byte-for-byte alone —
and counted, not silently dropped — when:

- **Workspace/intra-repo member.** Its name matches a sibling
  `[project].name` discovered under `--workspace-root`, an explicit
  `--skip` name, or the repo's own package name. Bumping a path/workspace
  dependency against PyPI is meaningless.
- **CVE-pinned security floor.** Its trailing `#` comment mentions "CVE" —
  treated as an intentional pinned floor, not staleness.
- **Complex spec.** It is a direct URL/VCS reference (contains `@`) or
  carries an environment marker (contains `;`) — these need human review,
  not a mechanical version swap.
- **Unresolvable on PyPI.** The name 404s, times out, or the network call
  otherwise fails. Reported in `errors`; never aborts the rest of the batch.

## Usage

```bash
python scripts/bump_dependencies.py <PATHS...> [--dry-run | --no-dry-run] [--commit]
    [--branch-prefix PREFIX] [--workspace-root DIR] [--skip NAME...]
    [--keep-caps] [--include-prerelease]
```

`PATHS` accepts any mix of repo directories (a `pyproject.toml` is expected
directly inside each), explicit `pyproject.toml` file paths, and glob
patterns (e.g. `agent-packages/agents/*`) — any set of repos.

**Modes** (`--dry-run` defaults on):

- No flags, or `--dry-run`: preview only — nothing is written, the JSON
  summary reports exactly what WOULD change (`package`, `from`, `to` per
  entry).
- `--no-dry-run`: write the bumped `pyproject.toml` files in place.
- `--commit` (implies write unless `--dry-run` is also explicitly given):
  additionally create `<branch-prefix><repo-name>` off `main`, commit that
  repo's `pyproject.toml`, and restore `main`. A repo with zero bumps is
  skipped entirely — no branch, no commit. An explicit `--dry-run` always
  wins over `--commit`, so `--dry-run --commit` safely previews what
  `--commit` would do.

**Other flags:**

- `--branch-prefix PREFIX` — branch name prefix for `--commit` (default
  `chore/bump-deps-`).
- `--workspace-root DIR` — scan `DIR` recursively for sibling
  `[project].name` values to auto-skip as workspace members.
- `--skip NAME...` — additional dependency names to skip, same treatment as
  an auto-detected workspace member.
- `--keep-caps` — append the original upper-bound clause verbatim after the
  new floor instead of dropping it (e.g. `>=2.0.0,<3.0.0`). The tool does not
  validate that the preserved cap is still satisfiable against the new floor
  — that is exactly what the two-phase `uv lock` reconciliation step catches.
- `--include-prerelease` — resolve the newest version including
  alpha/beta/rc/dev releases, instead of the newest stable release.

Exit code is `1` if any `errors` were recorded (path or per-package), `0`
otherwise — the run itself never aborts partway through the batch.

## Examples

Preview a bump for a single repo:

```bash
python scripts/bump_dependencies.py ~/code/my-service
```

Write the bump for a single repo without committing:

```bash
python scripts/bump_dependencies.py ~/code/my-service --no-dry-run
```

Fleet case — bump every agent package under a monorepo, skipping intra-repo
siblings, and land each changed repo on its own review branch:

```bash
python scripts/bump_dependencies.py \
    "/home/apps/workspace/agent-packages/agents/*" \
    "/home/apps/workspace/agent-packages/skills/*" \
    --workspace-root /home/apps/workspace/agent-packages \
    --commit --branch-prefix chore/bump-deps-
```

Preview a fleet bump that also considers prereleases, keeping any existing
upper caps:

```bash
python scripts/bump_dependencies.py "/home/apps/workspace/agent-packages/agents/*" \
    --keep-caps --include-prerelease
```

## Requirement

`tomlkit` is required and is intentionally **not** bundled as a package
extra of this repository — install it into whatever environment runs the
script, e.g. `pip install tomlkit` (a scratch/throwaway virtualenv is fine).
Running the script without it prints that instruction and exits instead of
failing with a bare traceback.

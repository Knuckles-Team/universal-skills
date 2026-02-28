---
name: github-tools
description: Consolidated skill for GitHub workflows and git practices. Use when managing PR comments, fixing CI failures, using the gh CLI for issues/PRs/workflow runs, finishing development branches, performing code review, or managing git worktrees. Do NOT use for general git operations that don't involve GitHub (use standard git commands instead).
categories: [Development]
tags: [github, git, pull-requests, ci, code-review, workflow, worktrees, gh-cli]
---

# GitHub & Git Workflow Tools

## Overview

Utilities for interacting with GitHub PRs, CI, issues, and Git workflows — including the `gh` CLI and custom scripts.

---

## 1. `gh` CLI — GitHub Native Interactions

Use the `gh` CLI to interact directly with GitHub. Always specify `--repo owner/repo` when not inside a git directory, or use URLs directly.

### Pull Requests

```bash
# Check CI status on a PR
gh pr checks 55 --repo owner/repo

# List open PRs
gh pr list --repo owner/repo

# View PR details
gh pr view 55 --repo owner/repo

# Merge a PR
gh pr merge 55 --repo owner/repo --squash
```

### Issues

```bash
# List open issues
gh issue list --repo owner/repo --limit 20

# Create an issue
gh issue create --repo owner/repo --title "Bug: ..." --body "Details..."

# Close an issue
gh issue close 42 --repo owner/repo
```

### Workflow Runs & CI

```bash
# List recent workflow runs
gh run list --repo owner/repo --limit 10

# View a specific run and see which steps ran
gh run view <run-id> --repo owner/repo

# View logs for failed steps only
gh run view <run-id> --repo owner/repo --log-failed

# Re-run failed jobs
gh run rerun <run-id> --repo owner/repo --failed
```

### Advanced API Queries

Use `gh api` for data not available through standard subcommands:

```bash
# Get PR with specific fields
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# List PR reviews
gh api repos/owner/repo/pulls/55/reviews --jq '.[].state'
```

### JSON Output & Filtering

Most `gh` commands support `--json` and `--jq` for structured output:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
gh pr list --repo owner/repo --json number,headRefName,author --jq '.[] | "\(.number) \(.headRefName) by \(.author.login)"'
```

---

## 2. Fetching PR Review Comments (`scripts/fetch_comments.py`)

Fetches and formats PR comments that need addressing. Run before making changes to respond to reviewers.

```bash
python scripts/fetch_comments.py <pr_url>
```

---

## 3. Inspecting CI Failures (`scripts/inspect_pr_checks.py`)

Inspects GitHub Actions checks on a PR and outputs logs of failing steps.

```bash
python scripts/inspect_pr_checks.py <pr_url>
```

---

## 4. Code Review Guidance

**When requesting review:**
- Ensure PR title is descriptive and clean
- Confirm tests pass locally
- PR description must explain the *why*, not just the what
- Keep PRs small and focused on one concern

**When receiving review:**
- Read feedback with technical rigor, not defensiveness
- Use `scripts/fetch_comments.py` to get all comments in one pass
- Respond to every comment (resolve or ask a clarifying question)

---

## 5. Git Worktrees

When switching branches to fix a bug while keeping current progress:

```bash
git worktree add ../my-new-branch my-new-branch
cd ../my-new-branch
# ... fix bug, commit ...
cd ../original-branch
git worktree remove ../my-new-branch
```

---

## 6. Finishing Branches (Pre-PR Checklist)

Before opening a PR:
1. Verify the code compiles/runs
2. Run formatters and linters
3. Review your own diff: `git diff main...HEAD`
4. Check CI locally if possible
5. Write a clear PR description explaining the intent

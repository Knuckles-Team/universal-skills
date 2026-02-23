---
name: github-tools
description: "Consolidated skill for GitHub workflows and git practices. Use this skill when addressing PR comments, fixing CI failures, finishing development branches, practicing code review, or managing git worktrees."
categories: [Development]
tags: [github, git, pull-requests, ci, code-review, workflow, worktrees]
---

# GitHub & Git Workflow Tools

## Overview

This skill combines multiple workflow utilities for interacting with Git and GitHub PRs.

## Capabilities/Tools
Fetches and formats PR comments that need to be addressed. Run this before making changes to respond to reviewers.
```bash
python scripts/fetch_comments.py <pr_url>
```

## 2. Fixing CI Tests (`scripts/inspect_pr_checks.py`)
Inspects the GitHub Actions (or other CI) checks on a PR and output logs of failing steps. Use this to debug why a PR is failing checks.
```bash
python scripts/inspect_pr_checks.py <pr_url>
```

## 3. Reviewing Code (`code-reviewer.md`)
Guidance on how to evaluate PRs, provide meaningful code reviews, or receive code review feedback.
- When *requesting* review: Ensure the PR title is clean, tests pass, and description explains the 'why'.
- When *receiving* review: Read feedback with technical rigor rather than performative agreement. Use the `fetch_comments.py` tool.

## 4. Git Worktrees
When jumping between branches to fix a bug while keeping your current progress, use git worktrees rather than stashing.
```bash
git worktree add ../my-new-branch my-new-branch
cd ../my-new-branch
```

## 5. Finishing Branches
Before opening a PR, always:
1. Verify the code compiles/runs.
2. Run standard formatters/linters.
3. Review your own diff (`git diff main...HEAD`).

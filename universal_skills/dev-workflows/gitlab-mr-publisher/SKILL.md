---
name: gitlab-mr-publisher
description: >
  Universal GitLab Merge Request publishing atomic skill. Branches, commits,
  pushes, and creates a Merge Request via GitLab API.
domain: dev-workflows
license: MIT
tags: [gitlab, git, pr, code-review]
metadata:
  author: Genius
  version: '0.1.0'
requires:
  - github-tools
---

# GitLab MR Publisher Skill

Stateless atomic operation to automate local Git synchronization, remote tracking setup, commit publishing, and high-fidelity GitLab Merge Request (MR) creation via API.

## Prerequisites

- `github-tools` — for Git branch validation, local branch/commit management, remote tracking mapping, and GitLab api wrappers/client operations.

## Steps

### Step 1: validate_git_state
Inspect the local Git workspace status and resolve publishing parameters:
- Query active repository status:
  - Confirm that the current directory is a valid Git repository.
  - Retrieve the current active branch name.
  - Assert the current branch is not a protected target branch (e.g. `main`, `master`, `production`, `stable`) to prevent direct pushes.
- Check workspace modifications:
  - Query for unstaged, staged, or untracked changes.
  - Determine if the repository has local commits that are ahead of the configured upstream remote.
  - If changes are present but uncommitted, compile a list of file changes and determine if they should be auto-committed using a provided semantic commit message.
- Output parameters:
  - `repo_root`: Absolute path of git repository.
  - `active_branch`: Current local branch name.
  - `has_commits_to_push`: Boolean flag indicating if commits are pending remote synchronization.

### Step 2: push_commits [depends_on: validate_git_state]
Publish local commits to the remote repository, setting up remote tracking upstream if necessary:
- Configure upstream tracking:
  - Query if the remote tracking branch exists for the current local branch on the configured target remote (usually `origin`).
  - If no upstream tracker exists, configure Git to establish a tracking branch on the remote: `git push --set-upstream origin <branch_name>`.
- Execute commit push:
  - Synchronize commits to the remote endpoint.
  - Validate push operation success by capturing CLI stream outputs and verifying zero authentication, branch-ahead, or hook failures.
- Output parameters:
  - `push_success`: Boolean indicating if pushing succeeded.
  - `remote_branch`: Full remote ref name.

### Step 3: spawn_merge_request [depends_on: push_commits]
Establish a high-fidelity Merge Request via the GitLab API:
- Resolve merge request parameters:
  - Target Project Path: GitLab path or numerical project ID.
  - Source Branch: Current local/remote branch that was pushed.
  - Target Branch: The destination branch for merge (default: `main` or `master`).
  - Title: Semantic title for the merge request.
  - Description: Markdown-formatted description summarizing the changes, user stories met, and validation checklists.
- Create GitLab MR:
  - Send POST request to GitLab `/projects/:id/merge_requests` API endpoint or use pre-configured GitLab client wrapper.
  - Set options such as: `remove_source_branch=true`, `squash=true`.
- Output summary:
  - `status`: "SUCCESS" or "FAILED"
  - `mr_iid`: Numerical GitLab internal ID of the created MR.
  - `mr_url`: Complete URL string to access the GitLab Merge Request interface.
  - `title`: Actual MR title published.

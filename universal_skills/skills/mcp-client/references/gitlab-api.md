# GitLab MCP Reference

**Project:** `gitlab-api`
**Entrypoint:** `gitlab-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITLAB_URL` | Required for authentication |
| `GITLAB_TOKEN` | Required for authentication |

## Available Tool Tags (19)

| Env Variable | Default |
|-------------|----------|
| `BRANCHESTOOL` | `True` |
| `COMMITSTOOL` | `True` |
| `CUSTOM_APITOOL` | `True` |
| `DEPLOY_TOKENSTOOL` | `True` |
| `ENVIRONMENTSTOOL` | `True` |
| `GROUPSTOOL` | `True` |
| `JOBSTOOL` | `True` |
| `MEMBERSTOOL` | `True` |
| `MERGE_REQUESTSTOOL` | `True` |
| `MERGE_RULESTOOL` | `True` |
| `MISCTOOL` | `True` |
| `PACKAGESTOOL` | `True` |
| `PIPELINESTOOL` | `True` |
| `PIPELINE_SCHEDULESTOOL` | `True` |
| `PROJECTSTOOL` | `True` |
| `PROTECTED_BRANCHESTOOL` | `True` |
| `RELEASESTOOL` | `True` |
| `RUNNERSTOOL` | `True` |
| `TAGSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "gitlab-api": {
      "command": "gitlab-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "GITLAB_URL": "${GITLAB_URL}",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "BRANCHESTOOL": "True",
        "COMMITSTOOL": "True",
        "CUSTOM_APITOOL": "True",
        "DEPLOY_TOKENSTOOL": "True",
        "ENVIRONMENTSTOOL": "True",
        "GROUPSTOOL": "True",
        "JOBSTOOL": "True",
        "MEMBERSTOOL": "True",
        "MERGE_REQUESTSTOOL": "True",
        "MERGE_RULESTOOL": "True",
        "MISCTOOL": "True",
        "PACKAGESTOOL": "True",
        "PIPELINESTOOL": "True",
        "PIPELINE_SCHEDULESTOOL": "True",
        "PROJECTSTOOL": "True",
        "PROTECTED_BRANCHESTOOL": "True",
        "RELEASESTOOL": "True",
        "RUNNERSTOOL": "True",
        "TAGSTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "gitlab-api": {
      "url": "http://gitlab-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `BRANCHESTOOL` and disable all others:

```json
{
  "mcpServers": {
    "gitlab-api": {
      "command": "gitlab-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "GITLAB_URL": "${GITLAB_URL}",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "BRANCHESTOOL": "True",
        "COMMITSTOOL": "False",
        "CUSTOM_APITOOL": "False",
        "DEPLOY_TOKENSTOOL": "False",
        "ENVIRONMENTSTOOL": "False",
        "GROUPSTOOL": "False",
        "JOBSTOOL": "False",
        "MEMBERSTOOL": "False",
        "MERGE_REQUESTSTOOL": "False",
        "MERGE_RULESTOOL": "False",
        "MISCTOOL": "False",
        "PACKAGESTOOL": "False",
        "PIPELINESTOOL": "False",
        "PIPELINE_SCHEDULESTOOL": "False",
        "PROJECTSTOOL": "False",
        "PROTECTED_BRANCHESTOOL": "False",
        "RELEASESTOOL": "False",
        "RUNNERSTOOL": "False",
        "TAGSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/gitlab-api.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command gitlab-mcp \
    --enable-tag BRANCHESTOOL \
    --all-tags "BRANCHESTOOL,COMMITSTOOL,CUSTOM_APITOOL,DEPLOY_TOKENSTOOL,ENVIRONMENTSTOOL,GROUPSTOOL,JOBSTOOL,MEMBERSTOOL,MERGE_REQUESTSTOOL,MERGE_RULESTOOL,MISCTOOL,PACKAGESTOOL,PIPELINESTOOL,PIPELINE_SCHEDULESTOOL,PROJECTSTOOL,PROTECTED_BRANCHESTOOL,RELEASESTOOL,RUNNERSTOOL,TAGSTOOL"
```

## Tailored Skills Reference

### test-skill

**Description:** A test skill.

## test-skill Skill

### When to use
For testing.

### How to use
Call it.

### Examples
- Example 1: ...

### gitlab-branches

**Description:** "Manages GitLab branches. Use for listing, creating, deleting, or querying branches in projects. Triggers: branch operations, git branching."

#### Overview
This skill handles branch-related tasks in GitLab via MCP tools. Focus on one operation per call for efficiency.

#### Available Tools
- `get_branches`: Get branches in a GitLab project, optionally filtered.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `search` (Optional[str]): Optional. - Filter branches by name containing this term
    - `regex` (Optional[str]): Optional. - Filter branches by regex pattern on name
    - `branch` (Optional[str]): Optional. - Branch name
- `create_branch`: Create a new branch in a GitLab project from a reference.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (str): Optional. - New branch name
    - `ref` (str): Optional. - Reference to create from (branch/tag/commit SHA)
- `delete_branch`: Delete a branch or all merged branches in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (Optional[str]): Optional. - Branch name to delete
    - `delete_merged_branches` (Optional[bool]): Optional. - Delete all merged branches (excluding protected)
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Identify the project_id (e.g., from query or prior context).
2. Call the appropriate tool with minimal params.
3. Handle pagination if results exceed limits (use MCP's built-in support).

#### Examples
- List branches: Call `get_branches` with project_id="my/project" and search="feature".
- Create: `create_branch` with project_id="123", branch="new-feature", ref="main".
- Delete merged: `delete_branch` with project_id="123", delete_merged_branches=true.

#### Error Handling
- Missing params: Retry with required fields.
- 404: Branch/project not found—verify IDs.
- Rate limits: Wait and retry.

### gitlab-commits

**Description:** "Manages GitLab commits. Use for listing, creating, reverting, or querying commit details/diffs/comments. Triggers: commit history, changes, reversions."

#### Overview
This skill covers commit operations via MCP. Use for code changes, diffs, or discussions.

#### Available Tools
- `get_commits`: Get commits in a GitLab project, optionally filtered.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (Optional[str]): Optional. - Commit SHA
    - `ref_name` (Optional[str]): Optional. - Branch, tag, or commit SHA to filter commits
    - `since` (Optional[str]): Optional. - Only commits after this date (ISO 8601 format)
    - `until` (Optional[str]): Optional. - Only commits before this date (ISO 8601 format)
    - `path` (Optional[str]): Optional. - Only commits that include this file path
    - `all` (Optional[bool]): Optional. - Include all commits across all branches
- `create_commit`: Create a new commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (str): Optional. - Branch name for the commit
    - `commit_message` (str): Optional. - Commit message
    - `actions` (List[Dict[str, str]]): Optional. - List of actions (create/update/delete files)
    - `author_email` (Optional[str]): Optional. - Author email for the commit
    - `author_name` (Optional[str]): Optional. - Author name for the commit
- `get_commit_diff`: Get the diff of a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `revert_commit`: Revert a commit in a target branch in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA to revert
    - `branch` (str): Optional. - Target branch to apply the revert
    - `dry_run` (Optional[bool]): Optional. - Simulate the revert without applying
- `get_commit_comments`: Retrieve comments on a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `create_commit_comment`: Create a new comment on a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `note` (str): Optional. - Content of the comment
    - `path` (Optional[str]): Optional. - File path to associate with the comment
    - `line` (Optional[int]): Optional. - Line number in the file for the comment
    - `line_type` (Optional[str]): Optional. - Type of line ('new' or 'old')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_commit_discussions`: Retrieve discussions (threaded comments) on a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_commit_statuses`: Retrieve build/CI statuses for a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ref` (Optional[str]): Optional. - Filter statuses by reference (branch or tag)
    - `stage` (Optional[str]): Optional. - Filter statuses by CI stage
    - `name` (Optional[str]): Optional. - Filter statuses by job name
    - `coverage` (Optional[bool]): Optional. - Include coverage information
    - `all` (Optional[bool]): Optional. - Include all statuses
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `post_build_status_to_commit`: Post a build/CI status to a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `state` (str): Optional. - State of the build (e.g., 'pending', 'running', 'success', 'failed')
    - `target_url` (Optional[str]): Optional. - URL to link to the build
    - `context` (Optional[str]): Optional. - Context of the status (e.g., 'ci/build')
    - `description` (Optional[str]): Optional. - Description of the status
    - `coverage` (Optional[float]): Optional. - Coverage percentage
    - `pipeline_id` (Optional[int]): Optional. - ID of the associated pipeline
    - `ref` (Optional[str]): Optional. - Reference (branch or tag) for the status
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_commit_merge_requests`: Retrieve merge requests associated with a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_commit_gpg_signature`: Retrieve the GPG signature for a specific commit in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `commit_hash` (str): Optional. - Commit SHA
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use project_id and commit_hash for specifics.
2. For creation, build actions list (e.g., [{"action": "create", "file_path": "file.txt", "content": "..."}]).
3. Async tools (e.g., delete) support progress via ctx.

#### Examples
- List commits: `get_commits` with project_id="123", ref_name="main", since="2023-01-01".
- Create: `create_commit` with project_id="123", branch="feature", commit_message="Add file", actions=[...].
- Revert: `revert_commit` with project_id="123", commit_hash="abc123", branch="main".

#### Error Handling
- Invalid ref: Check branch/SHA existence first.
- Conflicts: Use diff tools to resolve.

Reference `tools-reference.md` for schemas.

### gitlab-custom-api

**Description:** "Handles custom GitLab API requests. Use for any endpoint not covered by other skills. Triggers: advanced API calls, extensions."

#### Overview
Fallback for arbitrary requests.

#### Available Tools
- `api_request`: Make a custom API request to a GitLab instance.
  - **Parameters**:
    - `method` (str): Optional. - The HTTP method to use ('GET', 'POST', 'PUT', 'DELETE')
    - `endpoint` (str): Optional. - The API endpoint to send the request to
    - `data` (Optional[Dict[str, Any]]): Optional. - Data to include in the request body (for non-JSON payloads)
    - `json` (Optional[Dict[str, Any]]): Optional. - JSON data to include in the request body
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Specify method, endpoint, data/json.

#### Examples
- GET: `api_request` with method="GET", endpoint="projects/123/issues".
- POST: With data={"title": "New issue"}.

#### Error Handling
- Validate endpoints.

### gitlab-deploy-tokens

**Description:** "Manages GitLab deploy tokens. Use for creating, listing, or deleting tokens at instance, project, or group levels. Triggers: deploy keys, access tokens."

#### Overview
Handles deploy tokens for CI/CD access.

#### Available Tools
- `get_deploy_tokens`: Retrieve a list of all deploy tokens for the GitLab instance.
- `get_project_deploy_tokens`: Retrieve a list of deploy tokens for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `token_id` (Optional[int]): Optional. - Deploy token ID
- `create_project_deploy_token`: Create a deploy token for a GitLab project with specified name and scopes.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the deploy token
    - `scopes` (List[str]): Optional. - Scopes for the deploy token (e.g., ['read_repository'])
    - `expires_at` (Optional[str]): Optional. - Expiration date (ISO 8601 format)
    - `username` (Optional[str]): Optional. - Username associated with the token
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_project_deploy_token`: Delete a specific deploy token for a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `token_id` (int): Optional. - Deploy token ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_group_deploy_tokens`: Retrieve deploy tokens for a GitLab group (list or single by ID).
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `token_id` (Optional[int]): Optional. - Deploy token ID for single retrieval
- `create_group_deploy_token`: Create a deploy token for a GitLab group with specified name and scopes.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `name` (str): Optional. - Name of the deploy token
    - `scopes` (List[str]): Optional. - Scopes for the deploy token (e.g., ['read_repository'])
    - `expires_at` (Optional[str]): Optional. - Expiration date (ISO 8601 format)
    - `username` (Optional[str]): Optional. - Username associated with the token
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_group_deploy_token`: Delete a specific deploy token for a GitLab group.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `token_id` (int): Optional. - Deploy token ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Specify scopes as list (e.g., ["read_repository"]).
2. Use expires_at for time-bound tokens.

#### Examples
- Create project token: `create_project_deploy_token` with project_id="123", name="ci-token", scopes=["read_registry"].
- List group tokens: `get_group_deploy_tokens` with group_id="group/path".

#### Error Handling
- Duplicate names: Use unique names.
- Revocation: Delete to revoke.

### gitlab-environments

**Description:** "Manages GitLab environments. Use for creating, updating, deleting, or protecting deployment environments. Triggers: CI/CD environments, deployments."

#### Overview
Covers environment lifecycle and protection.

#### Available Tools
- `get_environments`: Retrieve a list of environments for a GitLab project, optionally filtered by name, search, or states or a single environment by id.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `environment_id` (Optional[int]): Optional. - Environment ID
    - `name` (Optional[str]): Optional. - Filter environments by exact name
    - `search` (Optional[str]): Optional. - Filter environments by search term in name
    - `states` (Optional[str]): Optional. - Filter environments by state (e.g., 'available', 'stopped')
- `create_environment`: Create a new environment in a GitLab project with a specified name and optional external URL.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the environment
    - `external_url` (Optional[str]): Optional. - External URL for the environment
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `update_environment`: Update an existing environment in a GitLab project with new name or external URL.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `environment_id` (int): Optional. - Environment ID
    - `name` (Optional[str]): Optional. - New name for the environment
    - `external_url` (Optional[str]): Optional. - New external URL for the environment
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_environment`: Delete a specific environment in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `environment_id` (int): Optional. - Environment ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `stop_environment`: Stop a specific environment in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `environment_id` (int): Optional. - Environment ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `stop_stale_environments`: Stop stale environments in a GitLab project, optionally filtered by older_than timestamp.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `older_than` (Optional[str]): Optional. - Filter environments older than this timestamp (ISO 8601 format)
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_stopped_environments`: Delete stopped review app environments in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_protected_environments`: Retrieve protected environments in a GitLab project (list or single by name).
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the protected environment
- `protect_environment`: Protect an environment in a GitLab project with optional approval count.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the environment to protect
    - `required_approval_count` (Optional[int]): Optional. - Number of approvals required for deployment
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `update_protected_environment`: Update a protected environment in a GitLab project with new approval count.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the protected environment
    - `required_approval_count` (Optional[int]): Optional. - New number of approvals required for deployment
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `unprotect_environment`: Unprotect a specific environment in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the environment to unprotect
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use name and external_url for creation.
2. Protection: Set required_approval_count.

#### Examples
- Create: `create_environment` with project_id="123", name="prod", external_url="https://prod.example.com".
- Protect: `protect_environment` with project_id="123", name="prod", required_approval_count=2.

#### Error Handling
- State conflicts: Check status before ops.

### gitlab-groups

**Description:** "Manages GitLab groups. Use for listing, editing groups, subgroups, projects, or merge requests. Triggers: group management, namespaces."

#### Overview
Handles group structures and contents.

#### Available Tools
- `get_groups`: Retrieve a list of groups, optionally filtered by search, sort, ownership, or access level or retrieve a single group by id.
  - **Parameters**:
    - `group_id` (Optional[str]): Optional. - Group ID or path
    - `search` (Optional[str]): Optional. - Filter groups by search term in name or path
    - `sort` (Optional[str]): Optional. - Sort order (e.g., 'asc', 'desc')
    - `order_by` (Optional[str]): Optional. - Field to sort by (e.g., 'name', 'path')
    - `owned` (Optional[bool]): Optional. - Filter groups owned by the authenticated user
    - `min_access_level` (Optional[int]): Optional. - Filter groups by minimum access level (e.g., 10 for Guest)
    - `top_level_only` (Optional[bool]): Optional. - Include only top-level groups (exclude subgroups)
- `edit_group`: Edit a specific GitLab group's details (name, path, description, or visibility).
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `name` (Optional[str]): Optional. - New name for the group
    - `path` (Optional[str]): Optional. - New path for the group
    - `description` (Optional[str]): Optional. - New description for the group
    - `visibility` (Optional[str]): Optional. - New visibility level (e.g., 'public', 'private')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_group_subgroups`: Retrieve a list of subgroups for a specific GitLab group, optionally filtered.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `search` (Optional[str]): Optional. - Filter subgroups by search term in name or path
    - `sort` (Optional[str]): Optional. - Sort order (e.g., 'asc', 'desc')
    - `order_by` (Optional[str]): Optional. - Field to sort by (e.g., 'name', 'path')
    - `owned` (Optional[bool]): Optional. - Filter subgroups owned by the authenticated user
- `get_group_descendant_groups`: Retrieve a list of all descendant groups for a specific GitLab group, optionally filtered.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `search` (Optional[str]): Optional. - Filter descendant groups by search term in name or path
    - `sort` (Optional[str]): Optional. - Sort order (e.g., 'asc', 'desc')
    - `order_by` (Optional[str]): Optional. - Field to sort by (e.g., 'name', 'path')
    - `owned` (Optional[bool]): Optional. - Filter descendant groups owned by the authenticated user
- `get_group_projects`: Retrieve a list of projects associated with a specific GitLab group, optionally including subgroups.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `include_subgroups` (Optional[bool]): Optional. - Include projects from subgroups
    - `search` (Optional[str]): Optional. - Filter projects by search term in name or path
    - `sort` (Optional[str]): Optional. - Sort order (e.g., 'asc', 'desc')
    - `order_by` (Optional[str]): Optional. - Field to sort by (e.g., 'name', 'path')
- `get_group_merge_requests`: Retrieve a list of merge requests associated with a specific GitLab group, optionally filtered.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `state` (Optional[str]): Optional. - Filter merge requests by state (e.g., 'opened', 'closed')
    - `scope` (Optional[str]): Optional. - Filter merge requests by scope (e.g., 'created_by_me')
    - `milestone` (Optional[str]): Optional. - Filter merge requests by milestone title
    - `search` (Optional[str]): Optional. - Filter merge requests by search term in title or description

#### Usage Instructions
1. Use group_id for specifics.
2. Filters: search, sort, owned.

#### Examples
- List subgroups: `get_group_subgroups` with group_id="mygroup".
- Get projects: `get_group_projects` with group_id="mygroup", include_subgroups=true.

#### Error Handling
- Access denied: Check permissions.

### gitlab-jobs

**Description:** "Manages GitLab CI jobs. Use for listing, logs, canceling, retrying, or erasing jobs. Triggers: CI builds, job status."

#### Overview
Covers job execution and logs.

#### Available Tools
- `get_project_jobs`: Retrieve a list of jobs for a specific GitLab project, optionally filtered by scope or a single job by id.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (Optional[int]): Optional. - Job ID
    - `scope` (Optional[str]): Optional. - Filter jobs by scope (e.g., 'success', 'failed')
    - `include_retried` (Optional[bool]): Optional. - Include retried jobs
    - `include_invisible` (Optional[bool]): Optional. - Include invisible jobs (e.g., from hidden pipelines)
- `get_project_job_log`: Retrieve the log (trace) of a specific job in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (int): Optional. - Job ID
- `cancel_project_job`: Cancel a specific job in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (int): Optional. - Job ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `retry_project_job`: Retry a specific job in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (int): Optional. - Job ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `erase_project_job`: Erase (delete artifacts and logs of) a specific job in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (int): Optional. - Job ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `run_project_job`: Run (play) a specific manual job in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `job_id` (int): Optional. - Job ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_pipeline_jobs`: Retrieve a list of jobs for a specific pipeline in a GitLab project, optionally filtered by scope.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_id` (int): Optional. - Pipeline ID
    - `scope` (Optional[str]): Optional. - Filter jobs by scope (e.g., 'success', 'failed')

#### Usage Instructions
1. Use job_id for actions.
2. Filters: scope, status.

#### Examples
- Get log: `get_project_job_log` with project_id="123", job_id=456.
- Retry: `retry_project_job` with project_id="123", job_id=456.

#### Error Handling
- Job not found: Verify IDs.

### gitlab-members

**Description:** "Manages GitLab members. Use for listing members in groups or projects. Triggers: user access, permissions."

#### Overview
Handles membership queries.

#### Available Tools
- `get_group_members`: Retrieve a list of members in a specific GitLab group, optionally filtered by query or user IDs.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `query` (Optional[str]): Optional. - Filter members by search term in name or username
    - `user_ids` (Optional[List[int]]): Optional. - Filter members by user IDs
    - `skip_users` (Optional[List[int]]): Optional. - Exclude specified user IDs
    - `show_seat_info` (Optional[bool]): Optional. - Include seat information for members
- `get_project_members`: Retrieve a list of members in a specific GitLab project, optionally filtered by query or user IDs.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `query` (Optional[str]): Optional. - Filter members by search term in name or username
    - `user_ids` (Optional[List[int]]): Optional. - Filter members by user IDs
    - `skip_users` (Optional[List[int]]): Optional. - Exclude specified user IDs

#### Usage Instructions
1. Filters: query, user_ids.

#### Examples
- Group members: `get_group_members` with group_id="mygroup", query="john".
- Project: Similar for projects.

#### Error Handling
- No members: Empty list is valid.

### gitlab-merge-requests

**Description:** "Manages GitLab merge requests. Use for creating, listing MRs across projects or groups. Triggers: PRs, code reviews."

#### Overview
Covers MR creation and queries.

#### Available Tools
- `create_merge_request`: Create a new merge request in a GitLab project with specified source and target branches.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `source_branch` (str): Optional. - Source branch for the merge request
    - `target_branch` (str): Optional. - Target branch for the merge request
    - `title` (str): Optional. - Title of the merge request
    - `description` (Optional[str]): Optional. - Description of the merge request
    - `assignee_id` (Optional[int]): Optional. - ID of the user to assign the merge request to
    - `reviewer_ids` (Optional[List[int]]): Optional. - IDs of users to set as reviewers
    - `labels` (Optional[List[str]]): Optional. - Labels to apply to the merge request
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_merge_requests`: Retrieve a list of merge requests across all projects, optionally filtered by state, scope, or labels.
  - **Parameters**:
    - `state` (Optional[str]): Optional. - Filter merge requests by state (e.g., 'opened', 'closed')
    - `scope` (Optional[str]): Optional. - Filter merge requests by scope (e.g., 'created_by_me')
    - `milestone` (Optional[str]): Optional. - Filter merge requests by milestone title
    - `view` (Optional[str]): Optional. - Filter merge requests by view (e.g., 'simple')
    - `labels` (Optional[List[str]]): Optional. - Filter merge requests by labels
    - `author_id` (Optional[int]): Optional. - Filter merge requests by author ID
- `get_project_merge_requests`: Retrieve a list of merge requests for a specific GitLab project, optionally filtered or a single merge request or a single merge request by merge id
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_id` (Optional[int]): Optional. - Merge request ID
    - `state` (Optional[str]): Optional. - Filter merge requests by state (e.g., 'opened', 'closed')
    - `scope` (Optional[str]): Optional. - Filter merge requests by scope (e.g., 'created_by_me')
    - `milestone` (Optional[str]): Optional. - Filter merge requests by milestone title
    - `labels` (Optional[List[str]]): Optional. - Filter merge requests by labels

#### Usage Instructions
1. For creation: source/target branches, title.

#### Examples
- Create: `create_merge_request` with project_id="123", source_branch="feature", target_branch="main", title="New feature".
- List: `get_project_merge_requests` with project_id="123", state="opened".

#### Error Handling
- Conflicts: Resolve before creation.

### gitlab-merge-rules

**Description:** "Manages GitLab merge approval rules. Use for approvals, rules at project/group levels. Triggers: code reviews, approvals."

#### Overview
Handles approval configurations.

#### Available Tools
- `get_project_level_merge_request_approval_rules`: Retrieve project-level merge request approval rules for a GitLab project details of a specific project-level merge request approval rule.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `approval_rule_id` (int): Optional. - Approval rule ID
- `create_project_level_rule`: Create a new project-level merge request approval rule.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the approval rule
    - `approvals_required` (Optional[int]): Optional. - Number of approvals required
    - `rule_type` (Optional[str]): Optional. - Type of rule (e.g., 'regular')
    - `user_ids` (Optional[List[int]]): Optional. - List of user IDs required to approve
    - `group_ids` (Optional[List[int]]): Optional. - List of group IDs required to approve
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `update_project_level_rule`: Update an existing project-level merge request approval rule.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `approval_rule_id` (int): Optional. - Approval rule ID
    - `name` (Optional[str]): Optional. - New name for the approval rule
    - `approvals_required` (Optional[int]): Optional. - New number of approvals required
    - `user_ids` (Optional[List[int]]): Optional. - Updated list of user IDs required to approve
    - `group_ids` (Optional[List[int]]): Optional. - Updated list of group IDs required to approve
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_project_level_rule`: Delete a project-level merge request approval rule.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `approval_rule_id` (int): Optional. - Approval rule ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `merge_request_level_approvals`: Retrieve approvals for a specific merge request in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_request_iid` (int): Optional. - Merge request IID
- `get_approval_state_merge_requests`: Retrieve the approval state of a specific merge request in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_request_iid` (int): Optional. - Merge request IID
- `get_merge_request_level_rules`: Retrieve merge request-level approval rules for a specific merge request in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_request_iid` (int): Optional. - Merge request IID
- `approve_merge_request`: Approve a specific merge request in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_request_iid` (int): Optional. - Merge request IID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `unapprove_merge_request`: Unapprove a specific merge request in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `merge_request_iid` (int): Optional. - Merge request IID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_group_level_rule`: Retrieve merge request approval settings for a specific GitLab group.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
- `edit_group_level_rule`: Edit merge request approval settings for a specific GitLab group.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `allow_author_approval` (Optional[bool]): Optional. - Whether authors can approve their own merge requests
    - `allow_committer_approval` (Optional[bool]): Optional. - Whether committers can approve merge requests
    - `allow_overrides_to_approver_list` (Optional[bool]): Optional. - Whether overrides to the approver list are allowed
    - `minimum_approvals` (Optional[int]): Optional. - Minimum number of approvals required
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_project_level_rule`: Retrieve merge request approval settings for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `edit_project_level_rule`: Edit merge request approval settings for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `allow_author_approval` (Optional[bool]): Optional. - Whether authors can approve their own merge requests
    - `allow_committer_approval` (Optional[bool]): Optional. - Whether committers can approve merge requests
    - `allow_overrides_to_approver_list` (Optional[bool]): Optional. - Whether overrides to the approver list are allowed
    - `minimum_approvals` (Optional[int]): Optional. - Minimum number of approvals required
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use approvals_required, user/group IDs.

#### Examples
- Create rule: `create_project_level_rule` with project_id="123", name="review", approvals_required=2.
- Approve MR: `approve_merge_request` with project_id="123", merge_request_iid=1.

#### Error Handling
- Insufficient approvals: Check state.

### gitlab-packages

**Description:** "Manages GitLab packages. Use for listing, publishing, or downloading packages. Triggers: artifact registry."

#### Overview
Covers package repository ops.

#### Available Tools
- `get_repository_packages`: Retrieve a list of repository packages for a specific GitLab project, optionally filtered by package type.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `package_type` (Optional[str]): Optional. - Filter packages by type (e.g., 'npm', 'maven')
- `publish_repository_package`: Publish a repository package to a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `package_name` (str): Optional. - Name of the package
    - `package_version` (str): Optional. - Version of the package
    - `file_name` (str): Optional. - Name of the package file
    - `status` (Optional[str]): Optional. - Status of the package (e.g., 'default', 'hidden')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `download_repository_package`: Download a repository package from a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `package_name` (str): Optional. - Name of the package
    - `package_version` (str): Optional. - Version of the package
    - `file_name` (str): Optional. - Name of the package file to download

#### Usage Instructions
1. Specify package_name/version/file_name.

#### Examples
- Publish: `publish_repository_package` with project_id="123", package_name="mypkg", package_version="1.0".
- Download: Similar with file_name.

#### Error Handling
- Version conflicts: Use unique versions.

### gitlab-pipeline-schedules

**Description:** "Manages GitLab pipeline schedules. Use for creating, editing, running scheduled pipelines. Triggers: cron jobs, automation."

#### Overview
Covers scheduled CI.

#### Available Tools
- `get_pipeline_schedules`: Retrieve a list of pipeline schedules for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `get_pipeline_schedule`: Retrieve details of a specific pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
- `get_pipelines_triggered_from_schedule`: Retrieve pipelines triggered by a specific pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
- `create_pipeline_schedule`: Create a pipeline schedule for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `description` (Optional[str]): Optional. - Description of the pipeline schedule
    - `ref` (str): Optional. - Reference (e.g., branch or tag) for the pipeline
    - `cron` (str): Optional. - Cron expression defining the schedule (e.g., '0 0 * * *')
    - `cron_timezone` (Optional[str]): Optional. - Timezone for the cron schedule (e.g., 'UTC')
    - `active` (Optional[bool]): Optional. - Whether the schedule is active
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `edit_pipeline_schedule`: Edit a pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `description` (Optional[str]): Optional. - New description of the pipeline schedule
    - `ref` (Optional[str]): Optional. - New reference (e.g., branch or tag) for the pipeline
    - `cron` (Optional[str]): Optional. - New cron expression for the schedule (e.g., '0 0 * * *')
    - `cron_timezone` (Optional[str]): Optional. - New timezone for the cron schedule (e.g., 'UTC')
    - `active` (Optional[bool]): Optional. - Whether the schedule is active
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `take_pipeline_schedule_ownership`: Take ownership of a pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_pipeline_schedule`: Delete a pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `run_pipeline_schedule`: Run a pipeline schedule immediately in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `create_pipeline_schedule_variable`: Create a variable for a pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `key` (str): Optional. - Key of the variable
    - `value` (str): Optional. - Value of the variable
    - `variable_type` (Optional[str]): Optional. - Type of variable (e.g., 'env_var')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_pipeline_schedule_variable`: Delete a variable from a pipeline schedule in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_schedule_id` (int): Optional. - Pipeline schedule ID
    - `key` (str): Optional. - Key of the variable to delete
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Cron format for schedules.

#### Examples
- Create: `create_pipeline_schedule` with project_id="123", ref="main", cron="0 0 * * *".
- Run: `run_pipeline_schedule` with pipeline_schedule_id=1.

#### Error Handling
- Invalid cron: Validate format.

### gitlab-pipelines

**Description:** "Manages GitLab pipelines. Use for listing, running pipelines. Triggers: CI triggers."

#### Overview
Handles pipeline execution.

#### Available Tools
- `get_pipelines`: Retrieve a list of pipelines for a specific GitLab project, optionally filtered by scope, status, or ref or details of a specific pipeline in a GitLab project..
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `pipeline_id` (Optional[int]): Optional. - Pipeline ID
    - `scope` (Optional[str]): Optional. - Filter pipelines by scope (e.g., 'running', 'branches')
    - `status` (Optional[str]): Optional. - Filter pipelines by status (e.g., 'success', 'failed')
    - `ref` (Optional[str]): Optional. - Filter pipelines by reference (e.g., branch or tag name)
    - `source` (Optional[str]): Optional. - Filter pipelines by source (e.g., 'push', 'schedule')
    - `updated_after` (Optional[str]): Optional. - Filter pipelines updated after this date (ISO 8601 format)
    - `updated_before` (Optional[str]): Optional. - Filter pipelines updated before this date (ISO 8601 format)
- `run_pipeline`: Run a pipeline for a specific GitLab project with a given reference (e.g., branch or tag).
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ref` (str): Optional. - Reference (e.g., branch or tag) to run the pipeline on
    - `variables` (Optional[Dict[str, str]]): Optional. - Dictionary of pipeline variables
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use ref for branch/tag.

#### Examples
- Run: `run_pipeline` with project_id="123", ref="main".
- List: `get_pipelines` with project_id="123", status="running".

#### Error Handling
- Failed triggers: Check config.

### gitlab-projects

**Description:** "Manages GitLab projects. Use for listing, editing, archiving, sharing projects. Triggers: repo management."

#### Overview
Handles project lifecycle.

#### Available Tools
- `get_projects`: Retrieve a list of projects, optionally filtered by ownership, search, sort, or visibility or Retrieve details of a specific GitLab project.
  - **Parameters**:
    - `project_id` (Optional[str]): Optional. - Project ID or path
    - `owned` (Optional[bool]): Optional. - Filter projects owned by the authenticated user
    - `search` (Optional[str]): Optional. - Filter projects by search term in name or path
    - `sort` (Optional[str]): Optional. - Sort projects by criteria (e.g., 'created_at', 'name')
    - `visibility` (Optional[str]): Optional. - Filter projects by visibility (e.g., 'public', 'private')
- `get_nested_projects_by_group`: Retrieve a list of nested projects within a GitLab group, including descendant groups.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
- `get_project_contributors`: Retrieve a list of contributors to a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `get_project_statistics`: Retrieve statistics for a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `edit_project`: Edit a specific GitLab project's details (name, description, or visibility).
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (Optional[str]): Optional. - New name of the project
    - `description` (Optional[str]): Optional. - New description of the project
    - `visibility` (Optional[str]): Optional. - New visibility of the project (e.g., 'public', 'private')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_project_groups`: Retrieve a list of groups associated with a specific GitLab project, optionally filtered.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `skip_groups` (Optional[List[int]]): Optional. - List of group IDs to exclude
    - `search` (Optional[str]): Optional. - Filter groups by search term in name
- `archive_project`: Archive a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `unarchive_project`: Unarchive a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_project`: Delete a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `share_project`: Share a specific GitLab project with a group, specifying access level.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `group_id` (str): Optional. - Group ID or path to share with
    - `group_access` (str): Optional. - Access level for the group (e.g., 'guest', 'developer', 'maintainer')
    - `expires_at` (Optional[str]): Optional. - Expiration date for the share in ISO 8601 format
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use visibility for updates.

#### Examples
- Edit: `edit_project` with project_id="123", visibility="public".
- Share: `share_project` with project_id="123", group_id="group", group_access="maintainer".

#### Error Handling
- Deletion permanent: Confirm first.

### gitlab-protected-branches

**Description:** "Manages protected branches in GitLab. Use for protecting/unprotecting branches, code owner approvals. Triggers: branch protection."

#### Overview
Secures branches.

#### Available Tools
- `get_protected_branches`: Retrieve a list of protected branches in a specific GitLab project or Retrieve details of a specific protected branch in a GitLab project..
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (Optional[str]): Optional. - Name of the branch to retrieve (e.g., 'main')
- `protect_branch`: Protect a specific branch in a GitLab project with specified access levels.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (str): Optional. - Name of the branch to protect (e.g., 'main')
    - `push_access_level` (Optional[str]): Optional. - Access level for pushing (e.g., 'maintainer')
    - `merge_access_level` (Optional[str]): Optional. - Access level for merging (e.g., 'developer')
    - `unprotect_access_level` (Optional[str]): Optional. - Access level for unprotecting (e.g., 'maintainer')
    - `allow_force_push` (Optional[bool]): Optional. - Whether force pushes are allowed
    - `allowed_to_push` (Optional[List[Dict]]): Optional. - List of users or groups allowed to push
    - `allowed_to_merge` (Optional[List[Dict]]): Optional. - List of users or groups allowed to merge
    - `allowed_to_unprotect` (Optional[List[Dict]]): Optional. - List of users or groups allowed to unprotect
    - `code_owner_approval_required` (Optional[bool]): Optional. - Whether code owner approval is required
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `unprotect_branch`: Unprotect a specific branch in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (str): Optional. - Name of the branch to unprotect (e.g., 'main')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `require_code_owner_approvals_single_branch`: Require or disable code owner approvals for a specific branch in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `branch` (str): Optional. - Name of the branch to set approval requirements for (e.g., 'main')
    - `code_owner_approval_required` (bool): Optional. - Whether code owner approval is required
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Access levels: push/merge.

#### Examples
- Protect: `protect_branch` with project_id="123", branch="main", push_access_level="maintainer".
- Code owners: `require_code_owner_approvals_single_branch` with code_owner_approval_required=true.

#### Error Handling
- Already protected: Update instead.

### gitlab-releases

**Description:** "Manages GitLab releases. Use for creating, updating, deleting releases and assets. Triggers: versioning, deployments."

#### Overview
Handles release artifacts.

#### Available Tools
- `get_releases`: Retrieve a list of releases for a specific GitLab project, optionally filtered.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `include_html_description` (Optional[bool]): Optional. - Whether to include HTML descriptions
    - `sort` (Optional[str]): Optional. - Sort releases by criteria (e.g., 'released_at')
    - `order_by` (Optional[str]): Optional. - Order releases by criteria (e.g., 'asc', 'desc')
- `get_latest_release`: Retrieve details of the latest release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `get_latest_release_evidence`: Retrieve evidence for the latest release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
- `get_latest_release_asset`: Retrieve a specific asset for the latest release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `direct_asset_path` (str): Optional. - Path to the asset (e.g., 'assets/file.zip')
- `get_group_releases`: Retrieve a list of releases for a specific GitLab group, optionally filtered.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `include_html_description` (Optional[bool]): Optional. - Whether to include HTML descriptions
    - `sort` (Optional[str]): Optional. - Sort releases by criteria (e.g., 'released_at')
    - `order_by` (Optional[str]): Optional. - Order releases by criteria (e.g., 'asc', 'desc')
- `download_release_asset`: Download a release asset from a group's release in GitLab.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `tag_name` (str): Optional. - Tag name of the release (e.g., 'v1.0.0')
    - `direct_asset_path` (str): Optional. - Path to the asset (e.g., 'assets/file.zip')
- `get_release_by_tag`: Retrieve details of a release by its tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `tag_name` (str): Optional. - Tag name of the release (e.g., 'v1.0.0')
- `create_release`: Create a new release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the release
    - `tag_name` (str): Optional. - Tag name associated with the release (e.g., 'v1.0.0')
    - `description` (Optional[str]): Optional. - Description of the release
    - `released_at` (Optional[str]): Optional. - Release date in ISO 8601 format
    - `assets` (Optional[Dict]): Optional. - Dictionary of release assets
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `create_release_evidence`: Create evidence for a release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `tag_name` (str): Optional. - Tag name of the release (e.g., 'v1.0.0')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `update_release`: Update a release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `tag_name` (str): Optional. - Tag name of the release to update (e.g., 'v1.0.0')
    - `name` (Optional[str]): Optional. - New name of the release
    - `description` (Optional[str]): Optional. - New description of the release
    - `released_at` (Optional[str]): Optional. - New release date in ISO 8601 format
    - `assets` (Optional[Dict]): Optional. - Updated dictionary of release assets
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_release`: Delete a release in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `tag_name` (str): Optional. - Tag name of the release to delete (e.g., 'v1.0.0')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Tag-based.

#### Examples
- Create: `create_release` with project_id="123", tag_name="v1.0", name="Version 1".
- Delete: `delete_release` with tag_name="v1.0".

#### Error Handling
- Tag missing: Create tag first.

### gitlab-runners

**Description:** "Manages GitLab runners. Use for registering, updating, deleting runners at various levels. Triggers: CI infrastructure."

#### Overview
Covers runner setup.

#### Available Tools
- `get_runners`: Retrieve a list of runners in GitLab, optionally filtered by scope, type, status, or tags or Retrieve details of a specific GitLab runner..
  - **Parameters**:
    - `runner_id` (Optional[int]): Optional. - ID of the runner to retrieve
    - `scope` (Optional[str]): Optional. - Filter runners by scope (e.g., 'active')
    - `type` (Optional[str]): Optional. - Filter runners by type (e.g., 'instance_type')
    - `status` (Optional[str]): Optional. - Filter runners by status (e.g., 'online')
    - `tag_list` (Optional[List[str]]): Optional. - Filter runners by tags
- `update_runner_details`: Update details for a specific GitLab runner.
  - **Parameters**:
    - `runner_id` (int): Optional. - ID of the runner to update
    - `description` (Optional[str]): Optional. - New description of the runner
    - `active` (Optional[bool]): Optional. - Whether the runner is active
    - `tag_list` (Optional[List[str]]): Optional. - List of tags for the runner
    - `run_untagged` (Optional[bool]): Optional. - Whether the runner can run untagged jobs
    - `locked` (Optional[bool]): Optional. - Whether the runner is locked
    - `access_level` (Optional[str]): Optional. - Access level of the runner (e.g., 'ref_protected')
    - `maximum_timeout` (Optional[int]): Optional. - Maximum timeout for the runner in seconds
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `pause_runner`: Pause or unpause a specific GitLab runner.
  - **Parameters**:
    - `runner_id` (int): Optional. - ID of the runner to pause or unpause
    - `active` (bool): Optional. - Whether the runner should be active (True) or paused (False)
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_runner_jobs`: Retrieve jobs for a specific GitLab runner, optionally filtered by status or sorted.
  - **Parameters**:
    - `runner_id` (int): Optional. - ID of the runner to retrieve jobs for
    - `status` (Optional[str]): Optional. - Filter jobs by status (e.g., 'success', 'failed')
    - `sort` (Optional[str]): Optional. - Sort jobs by criteria (e.g., 'created_at')
- `get_project_runners`: Retrieve a list of runners in a specific GitLab project, optionally filtered by scope.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `scope` (Optional[str]): Optional. - Filter runners by scope (e.g., 'active')
- `enable_project_runner`: Enable a runner in a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `runner_id` (int): Optional. - ID of the runner to enable
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_project_runner`: Delete a runner from a specific GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `runner_id` (int): Optional. - ID of the runner to delete
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_group_runners`: Retrieve a list of runners in a specific GitLab group, optionally filtered by scope.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `scope` (Optional[str]): Optional. - Filter runners by scope (e.g., 'active')
- `register_new_runner`: Register a new GitLab runner.
  - **Parameters**:
    - `token` (str): Optional. - Registration token for the runner
    - `description` (Optional[str]): Optional. - Description of the runner
    - `tag_list` (Optional[List[str]]): Optional. - List of tags for the runner
    - `run_untagged` (Optional[bool]): Optional. - Whether the runner can run untagged jobs
    - `locked` (Optional[bool]): Optional. - Whether the runner is locked
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_runner`: Delete a GitLab runner by ID or token.
  - **Parameters**:
    - `runner_id` (Optional[int]): Optional. - ID of the runner to delete
    - `token` (Optional[str]): Optional. - Token of the runner to delete
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `verify_runner_authentication`: Verify authentication for a GitLab runner using its token.
  - **Parameters**:
    - `token` (str): Optional. - Runner token to verify
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `reset_gitlab_runner_token`: Reset the GitLab runner registration token.
  - **Parameters**:
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `reset_project_runner_token`: Reset the registration token for a project's runner in GitLab.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `reset_group_runner_token`: Reset the registration token for a group's runner in GitLab.
  - **Parameters**:
    - `group_id` (str): Optional. - Group ID or path
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `reset_token`: Reset the authentication token for a specific GitLab runner.
  - **Parameters**:
    - `runner_id` (int): Optional. - ID of the runner to reset the token for
    - `token` (str): Optional. - Current token of the runner
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Use tokens for registration.

#### Examples
- Register: `register_new_runner` with token="abc123".
- Enable: `enable_project_runner` with runner_id=1.

#### Error Handling
- Token invalid: Reset.

### gitlab-tags

**Description:** "Manages GitLab tags. Use for creating, deleting, protecting tags. Triggers: versioning."

#### Overview
Handles tags and protection.

#### Available Tools
- `get_tags`: Retrieve a list of tags for a specific GitLab project, optionally filtered or sorted or Retrieve details of a specific tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (Optional[str]): Optional. - Name of the tag to retrieve (e.g., 'v1.0.0')
    - `search` (Optional[str]): Optional. - Filter tags by search term in name
    - `sort` (Optional[str]): Optional. - Sort tags by criteria (e.g., 'name', 'updated')
- `create_tag`: Create a new tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the tag to create (e.g., 'v1.0.0')
    - `ref` (str): Optional. - Reference (e.g., branch or commit SHA) to tag
    - `message` (Optional[str]): Optional. - Tag message
    - `release_description` (Optional[str]): Optional. - Release description associated with the tag
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `delete_tag`: Delete a specific tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the tag to delete (e.g., 'v1.0.0')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `get_protected_tags`: Retrieve a list of protected tags in a specific GitLab project, optionally filtered by name.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (Optional[str]): Optional. - Filter tags by name
- `get_protected_tag`: Retrieve details of a specific protected tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the protected tag to retrieve (e.g., 'v1.0.0')
- `protect_tag`: Protect a specific tag in a GitLab project with specified access levels.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the tag to protect (e.g., 'v1.0.0')
    - `create_access_level` (Optional[str]): Optional. - Access level for creating the tag (e.g., 'maintainer')
    - `allowed_to_create` (Optional[List[Dict]]): Optional. - List of users or groups allowed to create the tag
    - `ctx` (Optional[Context]): Optional. - MCP context for progress
- `unprotect_tag`: Unprotect a specific tag in a GitLab project.
  - **Parameters**:
    - `project_id` (str): Optional. - Project ID or path
    - `name` (str): Optional. - Name of the tag to unprotect (e.g., 'v1.0.0')
    - `ctx` (Optional[Context]): Optional. - MCP context for progress

#### Usage Instructions
1. Ref for creation.

#### Examples
- Create: `create_tag` with project_id="123", name="v1.0", ref="main".
- Protect: `protect_tag` with create_access_level="maintainer".

#### Error Handling
- Tag exists: Delete first.

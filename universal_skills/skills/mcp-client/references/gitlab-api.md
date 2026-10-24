# Gitlab Api Reference

**Project:** `gitlab-api`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITLAB_TOKEN` | Required for authentication |
| `GITLAB_URL` | Required for authentication |

## Available Tool Tags (19)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `BRANCHESTOOL` | `True` | (No tools found) |
| `COMMITSTOOL` | `True` | (No tools found) |
| `CUSTOM_APITOOL` | `True` | (No tools found) |
| `DEPLOY_TOKENSTOOL` | `True` | (No tools found) |
| `ENVIRONMENTSTOOL` | `True` | (No tools found) |
| `GROUPSTOOL` | `True` | (No tools found) |
| `JOBSTOOL` | `True` | (No tools found) |
| `MEMBERSTOOL` | `True` | (No tools found) |
| `MERGE_REQUESTSTOOL` | `True` | (No tools found) |
| `MERGE_RULESTOOL` | `True` | (No tools found) |
| `MISCTOOL` | `True` | (Internal tools) |
| `PACKAGESTOOL` | `True` | (No tools found) |
| `PIPELINESTOOL` | `True` | (No tools found) |
| `PIPELINE_SCHEDULESTOOL` | `True` | (No tools found) |
| `PROJECTSTOOL` | `True` | (No tools found) |
| `PROTECTED_BRANCHESTOOL` | `True` | (No tools found) |
| `RELEASESTOOL` | `True` | (No tools found) |
| `RUNNERSTOOL` | `True` | (No tools found) |
| `TAGSTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

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
        "GROUPSTOOL": "${ GROUPSTOOL:-True }",
        "PROTECTED_BRANCHESTOOL": "${ PROTECTED_BRANCHESTOOL:-True }",
        "PIPELINESTOOL": "${ PIPELINESTOOL:-True }",
        "MERGE_REQUESTSTOOL": "${ MERGE_REQUESTSTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "PACKAGESTOOL": "${ PACKAGESTOOL:-True }",
        "DEPLOY_TOKENSTOOL": "${ DEPLOY_TOKENSTOOL:-True }",
        "CUSTOM_APITOOL": "${ CUSTOM_APITOOL:-True }",
        "PIPELINE_SCHEDULESTOOL": "${ PIPELINE_SCHEDULESTOOL:-True }",
        "MERGE_RULESTOOL": "${ MERGE_RULESTOOL:-True }",
        "COMMITSTOOL": "${ COMMITSTOOL:-True }",
        "BRANCHESTOOL": "${ BRANCHESTOOL:-True }",
        "JOBSTOOL": "${ JOBSTOOL:-True }",
        "TAGSTOOL": "${ TAGSTOOL:-True }",
        "MEMBERSTOOL": "${ MEMBERSTOOL:-True }",
        "ENVIRONMENTSTOOL": "${ ENVIRONMENTSTOOL:-True }",
        "PROJECTSTOOL": "${ PROJECTSTOOL:-True }",
        "RELEASESTOOL": "${ RELEASESTOOL:-True }",
        "RUNNERSTOOL": "${ RUNNERSTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
gitlab-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only BRANCHESTOOL enabled:

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
        "GROUPSTOOL": "False",
        "PROTECTED_BRANCHESTOOL": "False",
        "PIPELINESTOOL": "False",
        "MERGE_REQUESTSTOOL": "False",
        "MISCTOOL": "False",
        "PACKAGESTOOL": "False",
        "DEPLOY_TOKENSTOOL": "False",
        "CUSTOM_APITOOL": "False",
        "PIPELINE_SCHEDULESTOOL": "False",
        "MERGE_RULESTOOL": "False",
        "COMMITSTOOL": "False",
        "BRANCHESTOOL": "True",
        "JOBSTOOL": "False",
        "TAGSTOOL": "False",
        "MEMBERSTOOL": "False",
        "ENVIRONMENTSTOOL": "False",
        "PROJECTSTOOL": "False",
        "RELEASESTOOL": "False",
        "RUNNERSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py gitlab-api help
```

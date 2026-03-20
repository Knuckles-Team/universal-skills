# Repository Manager Reference

**Project:** `repository-manager`

## Required Environment Variables

| Variable | Description |
|----------|-------------|


## Available Tool Tags (3)

## Available Tool Tags (3)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `FILE_OPERATIONSTOOL` | `True` | search_codebase |
| `GIT_OPERATIONSTOOL` | `True` | bump_version, clone_project, clone_projects, create_project, git_action, list_projects, pull_project, pull_projects, run_pre_commit |
| `MISCTOOL` | `True` | (Internal tools) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "repository-manager": {
      "command": "repository-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "FILE_OPERATIONSTOOL": "${ FILE_OPERATIONSTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "GIT_OPERATIONSTOOL": "${ GIT_OPERATIONSTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
repository-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only FILE_OPERATIONSTOOL enabled:

```json
{
  "mcpServers": {
    "repository-manager": {
      "command": "repository-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "FILE_OPERATIONSTOOL": "True",
        "MISCTOOL": "False",
        "GIT_OPERATIONSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py repository-manager help
```

# Archivebox Api Reference

**Project:** `archivebox-api`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ARCHIVEBOX_API_KEY` | API key for authentication |
| `ARCHIVEBOX_PASSWORD` | Password for authentication |
| `ARCHIVEBOX_TOKEN` | Bearer token for authentication |
| `ARCHIVEBOX_URL` | The URL of the ArchiveBox instance (e.g., https://yourinstance.archivebox.com) |
| `ARCHIVEBOX_USERNAME` | Username for authentication |
| `ARCHIVEBOX_VERIFY` | Required for authentication/configuration |

## Available Tool Tags (4)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `AUTHENTICATIONTOOL` | `True` | check_api_token, get_api_token |
| `CLITOOL` | `True` | cli_add, cli_list, cli_remove, cli_schedule, cli_update |
| `CORETOOL` | `True` | get_any, get_archiveresults, get_snapshot, get_snapshots, get_tag |
| `MISCTOOL` | `True` | (Internal tools) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "archivebox-mcp": {
      "command": "archivebox-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "ARCHIVEBOX_URL": "${ARCHIVEBOX_URL}",
        "ARCHIVEBOX_TOKEN": "${ARCHIVEBOX_TOKEN}",
        "ARCHIVEBOX_USERNAME": "${ARCHIVEBOX_USERNAME}",
        "ARCHIVEBOX_PASSWORD": "${ARCHIVEBOX_PASSWORD}",
        "ARCHIVEBOX_API_KEY": "${ARCHIVEBOX_API_KEY}",
        "ARCHIVEBOX_VERIFY": "${ARCHIVEBOX_VERIFY:-True}",
        "AUTHENTICATIONTOOL": "${ AUTHENTICATIONTOOL:-True }",
        "CLITOOL": "${ CLITOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "CORETOOL": "${ CORETOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
archivebox-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only AUTHENTICATIONTOOL enabled:

```json
{
  "mcpServers": {
    "archivebox-mcp": {
      "command": "archivebox-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "ARCHIVEBOX_URL": "${ARCHIVEBOX_URL}",
        "ARCHIVEBOX_TOKEN": "${ARCHIVEBOX_TOKEN}",
        "ARCHIVEBOX_USERNAME": "${ARCHIVEBOX_USERNAME}",
        "ARCHIVEBOX_PASSWORD": "${ARCHIVEBOX_PASSWORD}",
        "ARCHIVEBOX_API_KEY": "${ARCHIVEBOX_API_KEY}",
        "ARCHIVEBOX_VERIFY": "${ARCHIVEBOX_VERIFY:-True}",
        "AUTHENTICATIONTOOL": "True",
        "CLITOOL": "False",
        "MISCTOOL": "False",
        "CORETOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py archivebox-api help
```

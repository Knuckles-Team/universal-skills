# ArchiveBox Agent MCP Reference

**Project:** `archivebox-api`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ARCHIVEBOX_URL` | The URL of the ArchiveBox instance (e.g., https://yourinstance.archivebox.com) |
| `ARCHIVEBOX_TOKEN` | Bearer token for authentication |
| `ARCHIVEBOX_USERNAME` | Username for authentication |
| `ARCHIVEBOX_PASSWORD` | Password for authentication |
| `ARCHIVEBOX_API_KEY` | API key for authentication |

## Available Tool Tags (3)

| Env Variable | Default |
|-------------|----------|
| `AUTHENTICATIONTOOL` | `True` |
| `CORETOOL` | `True` |
| `CLITOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "archivebox-mcp": {
      "command": "archivebox-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "ARCHIVEBOX_URL": "${ARCHIVEBOX_URL}",
        "ARCHIVEBOX_TOKEN": "${ARCHIVEBOX_TOKEN}",
        "ARCHIVEBOX_USERNAME": "${ARCHIVEBOX_USERNAME}",
        "ARCHIVEBOX_PASSWORD": "${ARCHIVEBOX_PASSWORD}",
        "ARCHIVEBOX_API_KEY": "${ARCHIVEBOX_API_KEY}",
        "ARCHIVEBOX_VERIFY": "True",
        "AUTHENTICATIONTOOL": "True",
        "CORETOOL": "True",
        "CLITOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "archivebox-mcp" --tool "cli_add" --tool-args '{"urls": ["https://example.com"]}'
```

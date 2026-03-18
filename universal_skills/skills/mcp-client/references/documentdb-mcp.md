# DocumentDB MCP Reference

**Project:** `documentdb-mcp`
**Entrypoint:** `documentdb-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | Full MongoDB connection URI (optional if host/port used) |
| `MONGODB_HOST` | DocumentDB/MongoDB host |
| `MONGODB_PORT` | DocumentDB/MongoDB port |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `DOCUMENTDBTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "documentdb-mcp": {
      "command": "documentdb-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "MONGODB_URI": "${MONGODB_URI}",
        "MONGODB_HOST": "localhost",
        "MONGODB_PORT": "10260",
        "DOCUMENTDBTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "documentdb-mcp" --tool "list_collections" --tool-args '{"db_name": "test"}'
```

# Documentdb MCP Reference

**Project:** `documentdb-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_HOST` | DocumentDB/MongoDB host |
| `MONGODB_PORT` | DocumentDB/MongoDB port |
| `MONGODB_URI` | Full MongoDB connection URI (optional if host/port used) |

## Available Tool Tags (6)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ANALYSISTOOL` | `True` | (No tools found) |
| `COLLECTIONSTOOL` | `True` | (No tools found) |
| `CRUDTOOL` | `True` | (No tools found) |
| `MISCTOOL` | `True` | (Internal tools) |
| `SYSTEMTOOL` | `True` | (No tools found) |
| `USERSTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "documentdb-mcp": {
      "command": "documentdb-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MONGODB_URI": "${MONGODB_URI}",
        "MONGODB_HOST": "${MONGODB_HOST:-localhost}",
        "MONGODB_PORT": "${MONGODB_PORT:-10260}",
        "ANALYSISTOOL": "${ ANALYSISTOOL:-True }",
        "USERSTOOL": "${ USERSTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "COLLECTIONSTOOL": "${ COLLECTIONSTOOL:-True }",
        "CRUDTOOL": "${ CRUDTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
documentdb-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ANALYSISTOOL enabled:

```json
{
  "mcpServers": {
    "documentdb-mcp": {
      "command": "documentdb-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MONGODB_URI": "${MONGODB_URI}",
        "MONGODB_HOST": "${MONGODB_HOST:-localhost}",
        "MONGODB_PORT": "${MONGODB_PORT:-10260}",
        "ANALYSISTOOL": "True",
        "USERSTOOL": "False",
        "SYSTEMTOOL": "False",
        "COLLECTIONSTOOL": "False",
        "CRUDTOOL": "False",
        "MISCTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py documentdb-mcp help
```

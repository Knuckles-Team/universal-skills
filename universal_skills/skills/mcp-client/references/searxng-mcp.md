# Searxng MCP Reference

**Project:** `searxng-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SEARXNG_INSTANCE_URL` | URL of the SearXNG instance |
| `SEARXNG_PASSWORD` | Password for basic auth (optional) |
| `SEARXNG_USERNAME` | Username for basic auth (optional) |
| `USE_RANDOM_INSTANCE` | Whether to use a random public instance if no URL provided (True/False) |

## Available Tool Tags (2)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `MISCTOOL` | `True` | (Internal tools) |
| `SEARCHTOOL` | `True` | web_search |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "searxng-mcp": {
      "command": "searxng-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "SEARXNG_INSTANCE_URL": "${SEARXNG_INSTANCE_URL}",
        "SEARXNG_USERNAME": "${SEARXNG_USERNAME}",
        "SEARXNG_PASSWORD": "${SEARXNG_PASSWORD}",
        "USE_RANDOM_INSTANCE": "${USE_RANDOM_INSTANCE:-false}",
        "SEARCHTOOL": "${ SEARCHTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
searxng-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only MISCTOOL enabled:

```json
{
  "mcpServers": {
    "searxng-mcp": {
      "command": "searxng-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "SEARXNG_INSTANCE_URL": "${SEARXNG_INSTANCE_URL}",
        "SEARXNG_USERNAME": "${SEARXNG_USERNAME}",
        "SEARXNG_PASSWORD": "${SEARXNG_PASSWORD}",
        "USE_RANDOM_INSTANCE": "${USE_RANDOM_INSTANCE:-false}",
        "SEARCHTOOL": "False",
        "MISCTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py searxng-mcp help
```

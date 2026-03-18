# SearXNG MCP Reference

**Project:** `searxng-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SEARXNG_INSTANCE_URL` | URL of the SearXNG instance |
| `SEARXNG_USERNAME` | Username for basic auth (optional) |
| `SEARXNG_PASSWORD` | Password for basic auth (optional) |
| `USE_RANDOM_INSTANCE` | Whether to use a random public instance if no URL provided (True/False) |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `SEARXNGTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "searxng-mcp": {
      "command": "searxng-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "SEARXNG_INSTANCE_URL": "${SEARXNG_INSTANCE_URL}",
        "SEARXNG_USERNAME": "${SEARXNG_USERNAME}",
        "SEARXNG_PASSWORD": "${SEARXNG_PASSWORD}",
        "USE_RANDOM_INSTANCE": "false",
        "SEARXNGTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "searxng-mcp" --tool "search" --tool-args '{"query": "pydantic-ai"}'
```

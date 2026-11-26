# Plane MCP Reference

**Project:** `plane-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `PLANE_API_KEY` | Required for authentication/configuration |
| `PLANE_BASE_URL` | Required for authentication/configuration |
| `PLANE_WORKSPACE_SLUG` | Required for authentication/configuration |

## Available Tool Tags (0)

| Env Variable | Default | Tools |
|-------------|---------|-------|


## Stdio Connection (Default)

```text
server: plane-agent
command: uvx --transport stdio
env:
  PLANE_API_KEY: ${PLANE_API_KEY}
  PLANE_WORKSPACE_SLUG: ${PLANE_WORKSPACE_SLUG}
  PLANE_BASE_URL: ${PLANE_BASE_URL}
```

Register this command and environment in the server list of the MCP client in use.

## HTTP Connection

```bash
uvx --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py plane-agent help
```

# Postiz Agent MCP Reference

**Project:** `postiz-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `POSTIZ_URL` | Required for authentication (e.g., https://api.postiz.com/public/v1) |
| `POSTIZ_TOKEN` | Required for authentication (Public API Key or OAuth2 Token) |

## Available Tool Tags (5)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `INTEGRATIONSTOOL` | `True` | postiz-list-integrations, postiz-check-connection |
| `POSTSTOOL` | `True` | postiz-list-posts, postiz-create-post, postiz-delete-post |
| `UPLOADSTOOL` | `True` | postiz-upload-file |
| `ANALYTICSTOOL` | `True` | postiz-platform-analytics, postiz-post-analytics |
| `NOTIFICATIONSTOOL` | `True` | postiz-list-notifications |

## Stdio Connection (Default)

```text
server: postiz-agent
command: postiz-agent --transport stdio
env:
  POSTIZ_URL: ${POSTIZ_URL}
  POSTIZ_TOKEN: ${POSTIZ_TOKEN}
  INTEGRATIONSTOOL: ${ INTEGRATIONSTOOL:-True }
  POSTSTOOL: ${ POSTSTOOL:-True }
  UPLOADSTOOL: ${ UPLOADSTOOL:-True }
  ANALYTICSTOOL: ${ ANALYTICSTOOL:-True }
  NOTIFICATIONSTOOL: ${ NOTIFICATIONSTOOL:-True }
```

Register this command and environment in the server list of the MCP client in use.

## HTTP Connection

```bash
postiz-agent --transport sse --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only POSTSTOOL enabled:

```text
server: postiz-agent
command: postiz-agent --transport stdio
env:
  POSTIZ_URL: ${POSTIZ_URL}
  POSTIZ_TOKEN: ${POSTIZ_TOKEN}
  INTEGRATIONSTOOL: False
  POSTSTOOL: True
  UPLOADSTOOL: False
  ANALYTICSTOOL: False
  NOTIFICATIONSTOOL: False
```

Register this command and environment in the server list of the MCP client in use.

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py postiz-agent help
```

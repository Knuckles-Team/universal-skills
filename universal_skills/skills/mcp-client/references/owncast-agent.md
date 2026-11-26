# Owncast Agent MCP Reference

**Project:** `owncast-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `OWNCAST_URL` | Base URL of the Owncast instance (default: `http://localhost:8080`) |
| `OWNCAST_TOKEN` | Token for authentication |

## Available Tool Tags (2)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `STATUSTOOL` | `True` | owncast-get-status, owncast-get-config |
| `CHATTOOL` | `True` | owncast-send-chat-message, owncast-send-system-message, owncast-send-action-message, owncast-get-chat |

## Stdio Connection (Default)

```text
server: owncast-agent
command: owncast-agent --transport stdio
env:
  OWNCAST_URL: ${OWNCAST_URL}
  OWNCAST_TOKEN: ${OWNCAST_TOKEN}
  STATUSTOOL: ${ STATUSTOOL:-True }
  CHATTOOL: ${ CHATTOOL:-True }
```

Register this command and environment in the server list of the MCP client in use.

## HTTP Connection

```bash
owncast-agent --transport sse --host 0.0.0.0 --port 8000
```

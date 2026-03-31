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

```json
{
  "mcpServers": {
    "owncast-agent": {
      "command": "owncast-agent",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "OWNCAST_URL": "${OWNCAST_URL}",
        "OWNCAST_TOKEN": "${OWNCAST_TOKEN}",
        "STATUSTOOL": "${ STATUSTOOL:-True }",
        "CHATTOOL": "${ CHATTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
owncast-agent --transport sse --host 0.0.0.0 --port 8000
```

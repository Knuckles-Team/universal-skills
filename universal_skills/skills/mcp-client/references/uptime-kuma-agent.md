# Uptime Kuma Agent MCP Reference

**Project:** `uptime-kuma-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `UPTIME_KUMA_URL` | Base URL of the Uptime Kuma instance |
| `UPTIME_KUMA_TOKEN` | Token for authentication. For agent usage, you can provide `username:password` here or provide `UPTIME_KUMA_USERNAME` and `UPTIME_KUMA_PASSWORD` |

## Available Tool Tags (2)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `MONITORSTOOL` | `True` | uptime-kuma-get-monitors, uptime-kuma-get-monitor, uptime-kuma-add-monitor, uptime-kuma-edit-monitor, uptime-kuma-delete-monitor, uptime-kuma-pause-monitor, uptime-kuma-resume-monitor |
| `STATUSTOOL` | `True` | uptime-kuma-get-status, uptime-kuma-get-uptime |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "uptime-kuma-agent": {
      "command": "uptime-kuma-agent",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "UPTIME_KUMA_URL": "${UPTIME_KUMA_URL}",
        "UPTIME_KUMA_TOKEN": "${UPTIME_KUMA_TOKEN}",
        "MONITORSTOOL": "${ MONITORSTOOL:-True }",
        "STATUSTOOL": "${ STATUSTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
uptime-kuma-agent --transport sse --host 0.0.0.0 --port 8000
```

# Home Assistant Agent MCP Reference

**Project:** `home-assistant-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `HOME_ASSISTANT_URL` | Required for authentication (e.g., http://localhost:8123) |
| `HOME_ASSISTANT_TOKEN` | Required for authentication (Long-Lived Access Token) |

## Available Tool Tags (7)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `CONFIGTOOL` | `True` | ha-status, ha-config, ha-components |
| `STATESTOOL` | `True` | ha-list-states, ha-get-state |
| `SERVICESTOOL` | `True` | ha-list-services, ha-call-service |
| `EVENTSTOOL` | `True` | ha-list-events, ha-fire-event |
| `HISTORYTOOL` | `True` | ha-get-history |
| `LOGBOOKTOOL` | `True` | ha-get-logbook |
| `CALENDARTOOL` | `True` | ha-list-calendars, ha-get-calendar-events |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "home-assistant-agent": {
      "command": "home-assistant-agent",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "HOME_ASSISTANT_URL": "${HOME_ASSISTANT_URL}",
        "HOME_ASSISTANT_TOKEN": "${HOME_ASSISTANT_TOKEN}",
        "CONFIGTOOL": "${ CONFIGTOOL:-True }",
        "STATESTOOL": "${ STATESTOOL:-True }",
        "SERVICESTOOL": "${ SERVICESTOOL:-True }",
        "EVENTSTOOL": "${ EVENTSTOOL:-True }",
        "HISTORYTOOL": "${ HISTORYTOOL:-True }",
        "LOGBOOKTOOL": "${ LOGBOOKTOOL:-True }",
        "CALENDARTOOL": "${ CALENDARTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
home-assistant-agent --transport sse --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only STATESTOOL enabled:

```json
{
  "mcpServers": {
    "home-assistant-agent": {
      "command": "home-assistant-agent",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "HOME_ASSISTANT_URL": "${HOME_ASSISTANT_URL}",
        "HOME_ASSISTANT_TOKEN": "${HOME_ASSISTANT_TOKEN}",
        "CONFIGTOOL": "False",
        "STATESTOOL": "True",
        "SERVICESTOOL": "False",
        "EVENTSTOOL": "False",
        "HISTORYTOOL": "False",
        "LOGBOOKTOOL": "False",
        "CALENDARTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py home-assistant-agent help
```

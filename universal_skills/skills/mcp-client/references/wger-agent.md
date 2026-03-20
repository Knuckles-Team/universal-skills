# Wger Agent Reference

**Project:** `wger-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `WGER_ACCESS_TOKEN` | Permanent API token for authentication |
| `WGER_INSTANCE` | Wger instance URL (default: https://wger.de) |

## Available Tool Tags (7)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `BODYTOOL` | `True` | (No tools found) |
| `EXERCISETOOL` | `True` | (No tools found) |
| `NUTRITIONTOOL` | `True` | (No tools found) |
| `ROUTINECONFIGTOOL` | `True` | (No tools found) |
| `ROUTINETOOL` | `True` | (No tools found) |
| `USERTOOL` | `True` | (No tools found) |
| `WORKOUTTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "wger-agent": {
      "command": "wger-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "WGER_INSTANCE": "${WGER_INSTANCE}",
        "WGER_ACCESS_TOKEN": "${WGER_ACCESS_TOKEN}",
        "USERTOOL": "${ USERTOOL:-True }",
        "BODYTOOL": "${ BODYTOOL:-True }",
        "ROUTINETOOL": "${ ROUTINETOOL:-True }",
        "WORKOUTTOOL": "${ WORKOUTTOOL:-True }",
        "NUTRITIONTOOL": "${ NUTRITIONTOOL:-True }",
        "ROUTINECONFIGTOOL": "${ ROUTINECONFIGTOOL:-True }",
        "EXERCISETOOL": "${ EXERCISETOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
wger-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only BODYTOOL enabled:

```json
{
  "mcpServers": {
    "wger-agent": {
      "command": "wger-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "WGER_INSTANCE": "${WGER_INSTANCE}",
        "WGER_ACCESS_TOKEN": "${WGER_ACCESS_TOKEN}",
        "USERTOOL": "False",
        "BODYTOOL": "True",
        "ROUTINETOOL": "False",
        "WORKOUTTOOL": "False",
        "NUTRITIONTOOL": "False",
        "ROUTINECONFIGTOOL": "False",
        "EXERCISETOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py wger-agent help
```

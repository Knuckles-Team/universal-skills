# Portainer Agent Reference

**Project:** `portainer-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `PORTAINER_TOKEN` | API access token for authentication |
| `PORTAINER_URL` | Base URL of the Portainer instance (e.g., `http://localhost:9000`) |

## Available Tool Tags (10)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `AUTHTOOL` | `True` | (No tools found) |
| `DOCKERTOOL` | `True` | (No tools found) |
| `EDGETOOL` | `True` | (No tools found) |
| `ENVIRONMENTTOOL` | `True` | (No tools found) |
| `KUBERNETESTOOL` | `True` | (No tools found) |
| `REGISTRYTOOL` | `True` | (No tools found) |
| `STACKTOOL` | `True` | (No tools found) |
| `SYSTEMTOOL` | `True` | (No tools found) |
| `TEMPLATETOOL` | `True` | (No tools found) |
| `USERTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "portainer-agent": {
      "command": "portainer-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "PORTAINER_URL": "${PORTAINER_URL}",
        "PORTAINER_TOKEN": "${PORTAINER_TOKEN}",
        "AUTHTOOL": "${ AUTHTOOL:-True }",
        "USERTOOL": "${ USERTOOL:-True }",
        "DOCKERTOOL": "${ DOCKERTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "REGISTRYTOOL": "${ REGISTRYTOOL:-True }",
        "ENVIRONMENTTOOL": "${ ENVIRONMENTTOOL:-True }",
        "KUBERNETESTOOL": "${ KUBERNETESTOOL:-True }",
        "TEMPLATETOOL": "${ TEMPLATETOOL:-True }",
        "STACKTOOL": "${ STACKTOOL:-True }",
        "EDGETOOL": "${ EDGETOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
portainer-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only AUTHTOOL enabled:

```json
{
  "mcpServers": {
    "portainer-agent": {
      "command": "portainer-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "PORTAINER_URL": "${PORTAINER_URL}",
        "PORTAINER_TOKEN": "${PORTAINER_TOKEN}",
        "AUTHTOOL": "True",
        "USERTOOL": "False",
        "DOCKERTOOL": "False",
        "SYSTEMTOOL": "False",
        "REGISTRYTOOL": "False",
        "ENVIRONMENTTOOL": "False",
        "KUBERNETESTOOL": "False",
        "TEMPLATETOOL": "False",
        "STACKTOOL": "False",
        "EDGETOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py portainer-agent help
```

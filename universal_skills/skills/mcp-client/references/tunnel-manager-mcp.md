# Tunnel Manager MCP Reference

**Project:** `tunnel-manager`
**Entrypoint:** `tunnel-manager-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TUNNEL_IDENTITY_FILE` | Path to the SSH identity file for tunnel authentication |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `TUNNELMANAGERTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "tunnel-manager-mcp": {
      "command": "tunnel-manager-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "TUNNEL_IDENTITY_FILE": "${TUNNEL_IDENTITY_FILE}",
        "TUNNELMANAGERTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "tunnel-manager-mcp" --tool "list_tunnels"
```

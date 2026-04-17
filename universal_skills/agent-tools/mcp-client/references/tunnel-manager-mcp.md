# Tunnel Manager MCP Reference

**Project:** `tunnel-manager`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TUNNEL_IDENTITY_FILE` | Path to the SSH identity file for tunnel authentication |

## Available Tool Tags (3)

## Available Tool Tags (3)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `HOST_MANAGEMENTTOOL` | `True` | add_host, list_hosts, remove_host |
| `MISCTOOL` | `True` | (Internal tools) |
| `REMOTE_ACCESSTOOL` | `True` | check_ssh_server, configure_key_auth_on_inventory, copy_ssh_config, copy_ssh_config_on_inventory, receive_file_from_inventory, receive_file_from_remote_host, remove_host_key, rotate_ssh_key, rotate_ssh_key_on_inventory, run_command_on_inventory, run_command_on_remote_host, send_file_to_inventory, send_file_to_remote_host, setup_passwordless_ssh, test_key_auth |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "tunnel-manager-mcp": {
      "command": "tunnel-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TUNNEL_IDENTITY_FILE": "${TUNNEL_IDENTITY_FILE}",
        "HOST_MANAGEMENTTOOL": "${ HOST_MANAGEMENTTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "REMOTE_ACCESSTOOL": "${ REMOTE_ACCESSTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
tunnel-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only HOST_MANAGEMENTTOOL enabled:

```json
{
  "mcpServers": {
    "tunnel-manager-mcp": {
      "command": "tunnel-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TUNNEL_IDENTITY_FILE": "${TUNNEL_IDENTITY_FILE}",
        "HOST_MANAGEMENTTOOL": "True",
        "MISCTOOL": "False",
        "REMOTE_ACCESSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py tunnel-manager-mcp help
```

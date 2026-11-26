# Ansible Tower MCP Reference

**Project:** `ansible-tower-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ANSIBLE_TOWER_TOKEN` | Required for authentication |
| `ANSIBLE_TOWER_URL` | Required for authentication |

## Available Tool Tags (0)

| Env Variable | Default | Tools |
|-------------|---------|-------|

## Stdio Connection (Default)

```text
server: ansible-tower-mcp
command: ansible-tower-mcp --transport stdio
env:
  ANSIBLE_TOWER_URL: ${ANSIBLE_TOWER_URL}
  ANSIBLE_TOWER_TOKEN: ${ANSIBLE_TOWER_TOKEN}
```

Register this command and environment in the server list of the MCP client in use.

## HTTP Connection

```bash
ansible-tower-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py ansible-tower-mcp help
```

# Nextcloud Agent Reference

**Project:** `nextcloud-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXTCLOUD_PASSWORD` | Required for authentication |
| `NEXTCLOUD_URL` | Required for authentication |
| `NEXTCLOUD_USERNAME` | Required for authentication |

## Available Tool Tags (6)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `CALENDARTOOL` | `True` | create_calendar_event, list_calendar_events, list_calendars |
| `CONTACTSTOOL` | `True` | create_contact, list_address_books, list_contacts |
| `FILESTOOL` | `True` | copy_item, create_folder, delete_item, get_properties, health_check, list_files, move_item, read_file, write_file |
| `MISCTOOL` | `True` | (Internal tools) |
| `SHARINGTOOL` | `True` | create_share, delete_share, list_shares |
| `USERTOOL` | `True` | get_user_info |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "nextcloud-agent": {
      "command": "nextcloud-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "NEXTCLOUD_URL": "${NEXTCLOUD_URL}",
        "NEXTCLOUD_USERNAME": "${NEXTCLOUD_USERNAME}",
        "NEXTCLOUD_PASSWORD": "${NEXTCLOUD_PASSWORD}",
        "USERTOOL": "${ USERTOOL:-True }",
        "FILESTOOL": "${ FILESTOOL:-True }",
        "SHARINGTOOL": "${ SHARINGTOOL:-True }",
        "CALENDARTOOL": "${ CALENDARTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "CONTACTSTOOL": "${ CONTACTSTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
nextcloud-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only CALENDARTOOL enabled:

```json
{
  "mcpServers": {
    "nextcloud-agent": {
      "command": "nextcloud-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "NEXTCLOUD_URL": "${NEXTCLOUD_URL}",
        "NEXTCLOUD_USERNAME": "${NEXTCLOUD_USERNAME}",
        "NEXTCLOUD_PASSWORD": "${NEXTCLOUD_PASSWORD}",
        "USERTOOL": "False",
        "FILESTOOL": "False",
        "SHARINGTOOL": "False",
        "CALENDARTOOL": "True",
        "MISCTOOL": "False",
        "CONTACTSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py nextcloud-agent help
```

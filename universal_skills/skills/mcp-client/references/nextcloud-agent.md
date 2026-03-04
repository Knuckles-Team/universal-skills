# Nextcloud MCP Reference

**Project:** `nextcloud-agent`
**Entrypoint:** `nextcloud-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXTCLOUD_URL` | Required for authentication |
| `NEXTCLOUD_USERNAME` | Required for authentication |
| `NEXTCLOUD_PASSWORD` | Required for authentication |

## Available Tool Tags (6)

| Env Variable | Default |
|-------------|----------|
| `CALENDARTOOL` | `True` |
| `CONTACTSTOOL` | `True` |
| `FILESTOOL` | `True` |
| `MISCTOOL` | `True` |
| `SHARINGTOOL` | `True` |
| `USERTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

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
        "CALENDARTOOL": "True",
        "CONTACTSTOOL": "True",
        "FILESTOOL": "True",
        "MISCTOOL": "True",
        "SHARINGTOOL": "True",
        "USERTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "nextcloud-agent": {
      "url": "http://nextcloud-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `CALENDARTOOL` and disable all others:

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
        "CALENDARTOOL": "True",
        "CONTACTSTOOL": "False",
        "FILESTOOL": "False",
        "MISCTOOL": "False",
        "SHARINGTOOL": "False",
        "USERTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/nextcloud-agent.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command nextcloud-mcp \
    --enable-tag CALENDARTOOL \
    --all-tags "CALENDARTOOL,CONTACTSTOOL,FILESTOOL,MISCTOOL,SHARINGTOOL,USERTOOL"
```

## Tailored Skills Reference

### test-skill

**Description:** A test skill.

## test-skill Skill

### When to use
For testing.

### How to use
Call it.

### Examples
- Example 1: ...

### nextcloud-calendar

**Description:** "Generated skill for calendar operations. Contains 3 tools."

#### Overview
This skill handles operations related to calendar.

#### Available Tools
- `list_calendars`: List available calendars.
  - **Parameters**:
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `list_calendar_events`: List events in a calendar.
  - **Parameters**:
    - `calendar_url` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `create_calendar_event`: No description provided.
  - **Parameters**:
    - `calendar_url` (str)
    - `summary` (str)
    - `start_time` (str)
    - `end_time` (str)
    - `description` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### nextcloud-contacts

**Description:** "Generated skill for contacts operations. Contains 3 tools."

#### Overview
This skill handles operations related to contacts.

#### Available Tools
- `list_address_books`: List address books.
  - **Parameters**:
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `list_contacts`: List contacts in an address book.
  - **Parameters**:
    - `address_book_url` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `create_contact`: Create a new contact using raw vCard data.
  - **Parameters**:
    - `address_book_url` (str)
    - `vcard_data` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### nextcloud-dev-manual

**Description:** Developer manual for Nextcloud server version 14.

## Nextcloud Dev Manual Documentation

Developer manual for Nextcloud server version 14.

**Original Source**: [https://docs.nextcloud.com/server/14/developer_manual/](https://docs.nextcloud.com/server/14/developer_manual/)

**Contains**: 71 markdown files with full folder structure.
*Last updated: February 27, 2026*

### nextcloud-files

**Description:** "Generated skill for files operations. Contains 8 tools."

#### Overview
This skill handles operations related to files.

#### Available Tools
- `list_files`: List files and directories at a specific path in Nextcloud. Returns a formatted string list of contents.
  - **Parameters**:
    - `path` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `read_file`: Read the contents of a text file from Nextcloud.
  - **Parameters**:
    - `path` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `write_file`: Write text content to a file in Nextcloud.
  - **Parameters**:
    - `path` (str)
    - `content` (str)
    - `overwrite` (bool)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `create_folder`: Create a new directory in Nextcloud.
  - **Parameters**:
    - `path` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `delete_item`: Delete a file or directory in Nextcloud.
  - **Parameters**:
    - `path` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `move_item`: Move a file or directory to a new location.
  - **Parameters**:
    - `source` (str)
    - `destination` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `copy_item`: Copy a file or directory to a new location.
  - **Parameters**:
    - `source` (str)
    - `destination` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `get_properties`: Get detailed properties for a file or folder.
  - **Parameters**:
    - `path` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### nextcloud-sharing

**Description:** "Generated skill for sharing operations. Contains 3 tools."

#### Overview
This skill handles operations related to sharing.

#### Available Tools
- `list_shares`: List all shares.
  - **Parameters**:
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `create_share`: Create a new share.
  - **Parameters**:
    - `path` (str)
    - `share_type` (int)
    - `permissions` (int)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)
- `delete_share`: Delete a share.
  - **Parameters**:
    - `share_id` (str)
    - `base_url` (str)
    - `username` (str)
    - `password` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### nextcloud-user

**Description:** "Generated skill for user operations. Contains 1 tools."

#### Overview
This skill handles operations related to user.

#### Available Tools
- `get_user_info`: Get information about the current user.
  - **Parameters**:
    - `base_url` (str)
    - `username` (str)
    - `password` (str)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

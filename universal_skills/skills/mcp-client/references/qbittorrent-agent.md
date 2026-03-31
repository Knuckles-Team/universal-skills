# qBittorrent Manager MCP Reference

**Project:** `qbittorrent-agent`
**Entrypoint:** `python -m qbittorrent_agent.mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `QBITTORRENT_URL` | Base URL of the qBittorrent WebUI (e.g. http://localhost:8080) |
| `QBITTORRENT_USERNAME` | WebUI Username (default: admin) |
| `QBITTORRENT_PASSWORD` | WebUI Password (default: adminadmin) |

## Available Tool Tags (6)

| Env Variable | Default | Description |
|-------------|----------|-------------|
| `APPTOOL` | `True` | Application settings and versioning |
| `TORRENTSTOOL` | `True` | Torrent management (list, add, pause, resume, delete) |
| `TRANSFERTOOL` | `True` | Global transfer speed monitoring and limits |
| `RSSTOOL` | `True` | RSS feed and auto-downloading rule management |
| `SEARCHTOOL` | `True` | Torrent search plugin integration |
| `LOGTOOL` | `True` | Application log access |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "qbittorrent-agent": {
      "command": "python",
      "args": ["-m", "qbittorrent_agent.mcp", "--transport", "stdio"],
      "env": {
        "QBITTORRENT_URL": "${QBITTORRENT_URL}",
        "QBITTORRENT_USERNAME": "${QBITTORRENT_USERNAME}",
        "QBITTORRENT_PASSWORD": "${QBITTORRENT_PASSWORD}",
        "APPTOOL": "True",
        "TORRENTSTOOL": "True",
        "TRANSFERTOOL": "True",
        "RSSTOOL": "True",
        "SEARCHTOOL": "True",
        "LOGTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all tools
mcp-client qbittorrent-agent list_tools

# Get torrent list
mcp-client qbittorrent-agent get_torrents

# Search for content
mcp-client qbittorrent-agent search_start pattern="Ubuntu 22.04"
```

## Tailored Skills Reference

### [App] `app`
- `get_version`: Returns the qBittorrent version string.
- `get_preferences`: Returns detailed application settings.

### [Torrents] `torrents`
- `get_torrents`: Filters: `all`, `downloading`, `seeding`, `completed`, `paused`, `active`, `inactive`.
- `add_torrent`: Supports `urls` and optional parameters like `category`, `tags`, `savepath`.
- `pause_torrents`, `resume_torrents`, `delete_torrents`: Bulk operations by hash.

### [Transfer] `transfer`
- `get_transfer_info`: Global speeds and DHT node counts.

### [RSS] `rss`
- `get_rss_items`: List all feeds.
- `get_rss_rules`: List all auto-downloading rules.

### [Search] `search`
- `search_start`: Initiates a background search job.
- `search_status`: Monitors job progress.
- `search_results`: Fetches results for a specific job ID.

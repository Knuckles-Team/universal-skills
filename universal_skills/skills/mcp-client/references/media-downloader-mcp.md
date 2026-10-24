# Media Downloader MCP Reference

**Project:** `media-downloader`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `AUDIO_ONLY` | Whether to download only audio (True/False) |
| `DOWNLOAD_DIRECTORY` | Directory where downloaded media will be saved |

## Available Tool Tags (3)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `COLLECTION_MANAGEMENTTOOL` | `True` | download_media, run_command |
| `MISCTOOL` | `True` | (Internal tools) |
| `TEXT_EDITORTOOL` | `True` | text_editor |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "media-downloader-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DOWNLOAD_DIRECTORY": "${DOWNLOAD_DIRECTORY}",
        "AUDIO_ONLY": "${AUDIO_ONLY:-False}",
        "TEXT_EDITORTOOL": "${ TEXT_EDITORTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "COLLECTION_MANAGEMENTTOOL": "${ COLLECTION_MANAGEMENTTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
media-downloader-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only COLLECTION_MANAGEMENTTOOL enabled:

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "media-downloader-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DOWNLOAD_DIRECTORY": "${DOWNLOAD_DIRECTORY}",
        "AUDIO_ONLY": "${AUDIO_ONLY:-False}",
        "TEXT_EDITORTOOL": "False",
        "MISCTOOL": "False",
        "COLLECTION_MANAGEMENTTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py media-downloader-mcp help
```

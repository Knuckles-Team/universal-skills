# Media Downloader MCP Reference

**Project:** `media-downloader`
**Entrypoint:** `media-downloader-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DOWNLOAD_DIRECTORY` | Directory where downloaded media will be saved |
| `AUDIO_ONLY` | Whether to download only audio (True/False) |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `MEDIADOWNLOADERTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "media-downloader-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "DOWNLOAD_DIRECTORY": "${DOWNLOAD_DIRECTORY}",
        "AUDIO_ONLY": "False",
        "MEDIADOWNLOADERTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "media-downloader-mcp" --tool "download_video" --tool-args '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

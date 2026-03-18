# Audio Transcriber MCP Reference

**Project:** `audio-transcriber`
**Entrypoint:** `audio-transcriber-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TRANSCRIBE_DIRECTORY` | Directory where audio files are located and transcripts will be saved |
| `WHISPER_MODEL` | Whisper model to use (base, small, medium, large-v3) |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `AUDIOTRANSCRIBERTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "audio-transcriber-mcp": {
      "command": "audio-transcriber-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "TRANSCRIBE_DIRECTORY": "${TRANSCRIBE_DIRECTORY}",
        "WHISPER_MODEL": "base",
        "AUDIOTRANSCRIBERTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "audio-transcriber-mcp" --tool "transcribe_audio" --tool-args '{"file_path": "audio.mp3"}'
```

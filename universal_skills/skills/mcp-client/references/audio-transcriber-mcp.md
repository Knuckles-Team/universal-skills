# Audio Transcriber MCP Reference

**Project:** `audio-transcriber`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `TRANSCRIBE_DIRECTORY` | Directory where audio files are located and transcripts will be saved |
| `WHISPER_MODEL` | Whisper model to use (base, small, medium, large-v3) |

## Available Tool Tags (2)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `AUDIO_PROCESSINGTOOL` | `True` | transcribe_audio |
| `MISCTOOL` | `True` | (Internal tools) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "audio-transcriber-mcp": {
      "command": "audio-transcriber-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TRANSCRIBE_DIRECTORY": "${TRANSCRIBE_DIRECTORY}",
        "WHISPER_MODEL": "${WHISPER_MODEL:-base}",
        "AUDIO_PROCESSINGTOOL": "${ AUDIO_PROCESSINGTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
audio-transcriber-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only AUDIO_PROCESSINGTOOL enabled:

```json
{
  "mcpServers": {
    "audio-transcriber-mcp": {
      "command": "audio-transcriber-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TRANSCRIBE_DIRECTORY": "${TRANSCRIBE_DIRECTORY}",
        "WHISPER_MODEL": "${WHISPER_MODEL:-base}",
        "AUDIO_PROCESSINGTOOL": "True",
        "MISCTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py audio-transcriber-mcp help
```

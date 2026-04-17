# Langfuse Agent MCP Reference

**Project:** `langfuse-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `LANGFUSE_HOST` | Host URL (default: `https://cloud.langfuse.com`) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse Public Key |
| `LANGFUSE_SECRET_KEY` | Langfuse Secret Key |

## Available Tool Tags (2)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `TELEMETRYTOOL` | `True` | langfuse-get-traces, langfuse-get-metrics |
| `ANNOTATIONTOOL` | `True` | langfuse-get-annotation-queues |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "langfuse-agent": {
      "command": "langfuse-agent",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "LANGFUSE_HOST": "${LANGFUSE_HOST}",
        "LANGFUSE_PUBLIC_KEY": "${LANGFUSE_PUBLIC_KEY}",
        "LANGFUSE_SECRET_KEY": "${LANGFUSE_SECRET_KEY}",
        "TELEMETRYTOOL": "${ TELEMETRYTOOL:-True }",
        "ANNOTATIONTOOL": "${ ANNOTATIONTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
langfuse-agent --transport sse --host 0.0.0.0 --port 8000
```

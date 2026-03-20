# Stirlingpdf Agent Reference

**Project:** `stirlingpdf-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `STIRLINGPDF_API_KEY` | Required for authentication/configuration |
| `STIRLINGPDF_URL` | Required for authentication/configuration |

## Available Tool Tags (1)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `PDFTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "stirlingpdf-agent-mcp",
      "args": [],
      "env": {
        "STIRLINGPDF_URL": "${STIRLINGPDF_URL:-http://localhost:8080}",
        "STIRLINGPDF_API_KEY": "${STIRLINGPDF_API_KEY}",
        "PDFTOOL": "${ PDFTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
stirlingpdf-agent-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only PDFTOOL enabled:

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "stirlingpdf-agent-mcp",
      "args": [],
      "env": {
        "STIRLINGPDF_URL": "${STIRLINGPDF_URL:-http://localhost:8080}",
        "STIRLINGPDF_API_KEY": "${STIRLINGPDF_API_KEY}",
        "PDFTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py stirlingpdf-agent help
```

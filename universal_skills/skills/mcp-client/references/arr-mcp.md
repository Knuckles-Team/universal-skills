# Arr MCP Reference

**Project:** `arr-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `BAZARR_API_KEY` | Required for authentication/configuration |
| `BAZARR_BASE_URL` | Required for authentication/configuration |
| `CHAPTARR_API_KEY` | Required for authentication/configuration |
| `CHAPTARR_BASE_URL` | Required for authentication/configuration |
| `LIDARR_API_KEY` | Required for authentication/configuration |
| `LIDARR_BASE_URL` | Required for authentication/configuration |
| `PROWLARR_API_KEY` | Required for authentication/configuration |
| `PROWLARR_BASE_URL` | Required for authentication/configuration |
| `RADARR_API_KEY` | Required for authentication/configuration |
| `RADARR_BASE_URL` | Required for authentication/configuration |
| `SEERR_API_KEY` | Required for authentication/configuration |
| `SEERR_BASE_URL` | Required for authentication/configuration |
| `SONARR_API_KEY` | Required for authentication/configuration |
| `SONARR_BASE_URL` | Required for authentication/configuration |

## Available Tool Tags (51)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `BAZARR_CATALOGTOOL` | `True` | (No tools found) |
| `BAZARR_HISTORYTOOL` | `True` | (No tools found) |
| `BAZARR_SYSTEMTOOL` | `True` | (No tools found) |
| `CHAPTARR_CONFIGTOOL` | `True` | (No tools found) |
| `CHAPTARR_DOWNLOADSTOOL` | `True` | (No tools found) |
| `CHAPTARR_HISTORYTOOL` | `True` | (No tools found) |
| `CHAPTARR_INDEXERTOOL` | `True` | (No tools found) |
| `CHAPTARR_OPERATIONSTOOL` | `True` | (No tools found) |
| `CHAPTARR_PROFILESTOOL` | `True` | (No tools found) |
| `CHAPTARR_QUEUETOOL` | `True` | (No tools found) |
| `CHAPTARR_SEARCHTOOL` | `True` | (No tools found) |
| `CHAPTARR_SYSTEMTOOL` | `True` | (No tools found) |
| `LIDARR_CATALOGTOOL` | `True` | (No tools found) |
| `LIDARR_CONFIGTOOL` | `True` | (No tools found) |
| `LIDARR_DOWNLOADSTOOL` | `True` | (No tools found) |
| `LIDARR_HISTORYTOOL` | `True` | (No tools found) |
| `LIDARR_INDEXERTOOL` | `True` | (No tools found) |
| `LIDARR_OPERATIONSTOOL` | `True` | (No tools found) |
| `LIDARR_PROFILESTOOL` | `True` | (No tools found) |
| `LIDARR_QUEUETOOL` | `True` | (No tools found) |
| `LIDARR_SEARCHTOOL` | `True` | (No tools found) |
| `LIDARR_SYSTEMTOOL` | `True` | (No tools found) |
| `PROWLARR_CONFIGTOOL` | `True` | (No tools found) |
| `PROWLARR_DOWNLOADSTOOL` | `True` | (No tools found) |
| `PROWLARR_HISTORYTOOL` | `True` | (No tools found) |
| `PROWLARR_INDEXERTOOL` | `True` | (No tools found) |
| `PROWLARR_OPERATIONSTOOL` | `True` | (No tools found) |
| `PROWLARR_PROFILESTOOL` | `True` | (No tools found) |
| `PROWLARR_SEARCHTOOL` | `True` | (No tools found) |
| `PROWLARR_SYSTEMTOOL` | `True` | (No tools found) |
| `RADARR_CATALOGTOOL` | `True` | (No tools found) |
| `RADARR_CONFIGTOOL` | `True` | (No tools found) |
| `RADARR_DOWNLOADSTOOL` | `True` | (No tools found) |
| `RADARR_HISTORYTOOL` | `True` | (No tools found) |
| `RADARR_INDEXERTOOL` | `True` | (No tools found) |
| `RADARR_OPERATIONSTOOL` | `True` | (No tools found) |
| `RADARR_PROFILESTOOL` | `True` | (No tools found) |
| `RADARR_QUEUETOOL` | `True` | (No tools found) |
| `RADARR_SYSTEMTOOL` | `True` | (No tools found) |
| `SEERR_CATALOGTOOL` | `True` | (No tools found) |
| `SEERR_SEARCHTOOL` | `True` | (No tools found) |
| `SEERR_SYSTEMTOOL` | `True` | (No tools found) |
| `SONARR_CATALOGTOOL` | `True` | (No tools found) |
| `SONARR_CONFIGTOOL` | `True` | (No tools found) |
| `SONARR_DOWNLOADSTOOL` | `True` | (No tools found) |
| `SONARR_HISTORYTOOL` | `True` | (No tools found) |
| `SONARR_INDEXERTOOL` | `True` | (No tools found) |
| `SONARR_OPERATIONSTOOL` | `True` | (No tools found) |
| `SONARR_PROFILESTOOL` | `True` | (No tools found) |
| `SONARR_QUEUETOOL` | `True` | (No tools found) |
| `SONARR_SYSTEMTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "arr-mcp": {
      "command": "arr-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "RADARR_BASE_URL": "${RADARR_BASE_URL:-http://radarr:7878}",
        "RADARR_API_KEY": "${RADARR_API_KEY}",
        "SONARR_BASE_URL": "${SONARR_BASE_URL:-http://sonarr:8989}",
        "SONARR_API_KEY": "${SONARR_API_KEY}",
        "LIDARR_BASE_URL": "${LIDARR_BASE_URL:-http://lidarr:8686}",
        "LIDARR_API_KEY": "${LIDARR_API_KEY}",
        "PROWLARR_BASE_URL": "${PROWLARR_BASE_URL:-http://prowlarr:9696}",
        "PROWLARR_API_KEY": "${PROWLARR_API_KEY}",
        "BAZARR_BASE_URL": "${BAZARR_BASE_URL:-http://bazarr:6767}",
        "BAZARR_API_KEY": "${BAZARR_API_KEY}",
        "SEERR_BASE_URL": "${SEERR_BASE_URL:-http://seerr:5055}",
        "SEERR_API_KEY": "${SEERR_API_KEY}",
        "CHAPTARR_BASE_URL": "${CHAPTARR_BASE_URL:-http://chaptarr:8060}",
        "CHAPTARR_API_KEY": "${CHAPTARR_API_KEY}",
        "SONARR_DOWNLOADSTOOL": "${ SONARR_DOWNLOADSTOOL:-True }",
        "PROWLARR_SYSTEMTOOL": "${ PROWLARR_SYSTEMTOOL:-True }",
        "PROWLARR_HISTORYTOOL": "${ PROWLARR_HISTORYTOOL:-True }",
        "CHAPTARR_QUEUETOOL": "${ CHAPTARR_QUEUETOOL:-True }",
        "PROWLARR_SEARCHTOOL": "${ PROWLARR_SEARCHTOOL:-True }",
        "LIDARR_CONFIGTOOL": "${ LIDARR_CONFIGTOOL:-True }",
        "SONARR_SYSTEMTOOL": "${ SONARR_SYSTEMTOOL:-True }",
        "SONARR_PROFILESTOOL": "${ SONARR_PROFILESTOOL:-True }",
        "LIDARR_HISTORYTOOL": "${ LIDARR_HISTORYTOOL:-True }",
        "LIDARR_CATALOGTOOL": "${ LIDARR_CATALOGTOOL:-True }",
        "BAZARR_CATALOGTOOL": "${ BAZARR_CATALOGTOOL:-True }",
        "BAZARR_HISTORYTOOL": "${ BAZARR_HISTORYTOOL:-True }",
        "SONARR_HISTORYTOOL": "${ SONARR_HISTORYTOOL:-True }",
        "SONARR_QUEUETOOL": "${ SONARR_QUEUETOOL:-True }",
        "RADARR_DOWNLOADSTOOL": "${ RADARR_DOWNLOADSTOOL:-True }",
        "CHAPTARR_DOWNLOADSTOOL": "${ CHAPTARR_DOWNLOADSTOOL:-True }",
        "CHAPTARR_HISTORYTOOL": "${ CHAPTARR_HISTORYTOOL:-True }",
        "LIDARR_DOWNLOADSTOOL": "${ LIDARR_DOWNLOADSTOOL:-True }",
        "LIDARR_PROFILESTOOL": "${ LIDARR_PROFILESTOOL:-True }",
        "CHAPTARR_CONFIGTOOL": "${ CHAPTARR_CONFIGTOOL:-True }",
        "RADARR_INDEXERTOOL": "${ RADARR_INDEXERTOOL:-True }",
        "CHAPTARR_INDEXERTOOL": "${ CHAPTARR_INDEXERTOOL:-True }",
        "RADARR_CATALOGTOOL": "${ RADARR_CATALOGTOOL:-True }",
        "RADARR_PROFILESTOOL": "${ RADARR_PROFILESTOOL:-True }",
        "BAZARR_SYSTEMTOOL": "${ BAZARR_SYSTEMTOOL:-True }",
        "CHAPTARR_PROFILESTOOL": "${ CHAPTARR_PROFILESTOOL:-True }",
        "LIDARR_INDEXERTOOL": "${ LIDARR_INDEXERTOOL:-True }",
        "SEERR_SYSTEMTOOL": "${ SEERR_SYSTEMTOOL:-True }",
        "CHAPTARR_SEARCHTOOL": "${ CHAPTARR_SEARCHTOOL:-True }",
        "RADARR_HISTORYTOOL": "${ RADARR_HISTORYTOOL:-True }",
        "PROWLARR_CONFIGTOOL": "${ PROWLARR_CONFIGTOOL:-True }",
        "SONARR_CONFIGTOOL": "${ SONARR_CONFIGTOOL:-True }",
        "CHAPTARR_OPERATIONSTOOL": "${ CHAPTARR_OPERATIONSTOOL:-True }",
        "SEERR_CATALOGTOOL": "${ SEERR_CATALOGTOOL:-True }",
        "PROWLARR_INDEXERTOOL": "${ PROWLARR_INDEXERTOOL:-True }",
        "PROWLARR_OPERATIONSTOOL": "${ PROWLARR_OPERATIONSTOOL:-True }",
        "PROWLARR_DOWNLOADSTOOL": "${ PROWLARR_DOWNLOADSTOOL:-True }",
        "RADARR_CONFIGTOOL": "${ RADARR_CONFIGTOOL:-True }",
        "PROWLARR_PROFILESTOOL": "${ PROWLARR_PROFILESTOOL:-True }",
        "SONARR_CATALOGTOOL": "${ SONARR_CATALOGTOOL:-True }",
        "SONARR_INDEXERTOOL": "${ SONARR_INDEXERTOOL:-True }",
        "SONARR_OPERATIONSTOOL": "${ SONARR_OPERATIONSTOOL:-True }",
        "LIDARR_SYSTEMTOOL": "${ LIDARR_SYSTEMTOOL:-True }",
        "RADARR_SYSTEMTOOL": "${ RADARR_SYSTEMTOOL:-True }",
        "RADARR_QUEUETOOL": "${ RADARR_QUEUETOOL:-True }",
        "LIDARR_QUEUETOOL": "${ LIDARR_QUEUETOOL:-True }",
        "SEERR_SEARCHTOOL": "${ SEERR_SEARCHTOOL:-True }",
        "CHAPTARR_SYSTEMTOOL": "${ CHAPTARR_SYSTEMTOOL:-True }",
        "RADARR_OPERATIONSTOOL": "${ RADARR_OPERATIONSTOOL:-True }",
        "LIDARR_OPERATIONSTOOL": "${ LIDARR_OPERATIONSTOOL:-True }",
        "LIDARR_SEARCHTOOL": "${ LIDARR_SEARCHTOOL:-True }"
      },
      "timeout": 3600000
    }
  }
}
```

## HTTP Connection

```bash
arr-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only BAZARR_CATALOGTOOL enabled:

```json
{
  "mcpServers": {
    "arr-mcp": {
      "command": "arr-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "RADARR_BASE_URL": "${RADARR_BASE_URL:-http://radarr:7878}",
        "RADARR_API_KEY": "${RADARR_API_KEY}",
        "SONARR_BASE_URL": "${SONARR_BASE_URL:-http://sonarr:8989}",
        "SONARR_API_KEY": "${SONARR_API_KEY}",
        "LIDARR_BASE_URL": "${LIDARR_BASE_URL:-http://lidarr:8686}",
        "LIDARR_API_KEY": "${LIDARR_API_KEY}",
        "PROWLARR_BASE_URL": "${PROWLARR_BASE_URL:-http://prowlarr:9696}",
        "PROWLARR_API_KEY": "${PROWLARR_API_KEY}",
        "BAZARR_BASE_URL": "${BAZARR_BASE_URL:-http://bazarr:6767}",
        "BAZARR_API_KEY": "${BAZARR_API_KEY}",
        "SEERR_BASE_URL": "${SEERR_BASE_URL:-http://seerr:5055}",
        "SEERR_API_KEY": "${SEERR_API_KEY}",
        "CHAPTARR_BASE_URL": "${CHAPTARR_BASE_URL:-http://chaptarr:8060}",
        "CHAPTARR_API_KEY": "${CHAPTARR_API_KEY}",
        "SONARR_DOWNLOADSTOOL": "False",
        "PROWLARR_SYSTEMTOOL": "False",
        "PROWLARR_HISTORYTOOL": "False",
        "CHAPTARR_QUEUETOOL": "False",
        "PROWLARR_SEARCHTOOL": "False",
        "LIDARR_CONFIGTOOL": "False",
        "SONARR_SYSTEMTOOL": "False",
        "SONARR_PROFILESTOOL": "False",
        "LIDARR_HISTORYTOOL": "False",
        "LIDARR_CATALOGTOOL": "False",
        "BAZARR_CATALOGTOOL": "True",
        "BAZARR_HISTORYTOOL": "False",
        "SONARR_HISTORYTOOL": "False",
        "SONARR_QUEUETOOL": "False",
        "RADARR_DOWNLOADSTOOL": "False",
        "CHAPTARR_DOWNLOADSTOOL": "False",
        "CHAPTARR_HISTORYTOOL": "False",
        "LIDARR_DOWNLOADSTOOL": "False",
        "LIDARR_PROFILESTOOL": "False",
        "CHAPTARR_CONFIGTOOL": "False",
        "RADARR_INDEXERTOOL": "False",
        "CHAPTARR_INDEXERTOOL": "False",
        "RADARR_CATALOGTOOL": "False",
        "RADARR_PROFILESTOOL": "False",
        "BAZARR_SYSTEMTOOL": "False",
        "CHAPTARR_PROFILESTOOL": "False",
        "LIDARR_INDEXERTOOL": "False",
        "SEERR_SYSTEMTOOL": "False",
        "CHAPTARR_SEARCHTOOL": "False",
        "RADARR_HISTORYTOOL": "False",
        "PROWLARR_CONFIGTOOL": "False",
        "SONARR_CONFIGTOOL": "False",
        "CHAPTARR_OPERATIONSTOOL": "False",
        "SEERR_CATALOGTOOL": "False",
        "PROWLARR_INDEXERTOOL": "False",
        "PROWLARR_OPERATIONSTOOL": "False",
        "PROWLARR_DOWNLOADSTOOL": "False",
        "RADARR_CONFIGTOOL": "False",
        "PROWLARR_PROFILESTOOL": "False",
        "SONARR_CATALOGTOOL": "False",
        "SONARR_INDEXERTOOL": "False",
        "SONARR_OPERATIONSTOOL": "False",
        "LIDARR_SYSTEMTOOL": "False",
        "RADARR_SYSTEMTOOL": "False",
        "RADARR_QUEUETOOL": "False",
        "LIDARR_QUEUETOOL": "False",
        "SEERR_SEARCHTOOL": "False",
        "CHAPTARR_SYSTEMTOOL": "False",
        "RADARR_OPERATIONSTOOL": "False",
        "LIDARR_OPERATIONSTOOL": "False",
        "LIDARR_SEARCHTOOL": "False"
      },
      "timeout": 3600000
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py arr-mcp help
```

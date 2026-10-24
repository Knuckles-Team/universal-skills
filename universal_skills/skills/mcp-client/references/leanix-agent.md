# Leanix Agent Reference

**Project:** `leanix-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `LEANIX_API_TOKEN` | Required for API authentication |
| `LEANIX_WORKSPACE` | Required for authentication (e.g. https://app.leanix.net) |

## Available Tool Tags (32)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `GRAPHQLTOOL` | `True` | health_check |
| `LEANIX_AI_INVENTORY_BUILDERTOOL` | `True` | (No tools found) |
| `LEANIX_APPTIO_CONNECTORTOOL` | `True` | (No tools found) |
| `LEANIX_AUTOMATIONSTOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_AI_AGENTSTOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_LINKING_V1TOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_LINKING_V2TOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_SAASTOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_SAPTOOL` | `True` | (No tools found) |
| `LEANIX_DISCOVERY_SAP_EXTENSIONTOOL` | `True` | (No tools found) |
| `LEANIX_DOCUMENTSTOOL` | `True` | (No tools found) |
| `LEANIX_IMPACTSTOOL` | `True` | (No tools found) |
| `LEANIX_INTEGRATION_APITOOL` | `True` | (No tools found) |
| `LEANIX_INTEGRATION_COLLIBRATOOL` | `True` | (No tools found) |
| `LEANIX_INTEGRATION_SERVICENOWTOOL` | `True` | (No tools found) |
| `LEANIX_INTEGRATION_SIGNAVIOTOOL` | `True` | (No tools found) |
| `LEANIX_INVENTORY_DATA_QUALITYTOOL` | `True` | (No tools found) |
| `LEANIX_MANAGED_CODE_EXECUTIONTOOL` | `True` | (No tools found) |
| `LEANIX_METRICSTOOL` | `True` | (No tools found) |
| `LEANIX_MTMTOOL` | `True` | (No tools found) |
| `LEANIX_NAVIGATIONTOOL` | `True` | (No tools found) |
| `LEANIX_PATHFINDERTOOL` | `True` | (No tools found) |
| `LEANIX_POLLTOOL` | `True` | (No tools found) |
| `LEANIX_REFERENCE_DATATOOL` | `True` | (No tools found) |
| `LEANIX_REFERENCE_DATA_CATALOGTOOL` | `True` | (No tools found) |
| `LEANIX_STORAGETOOL` | `True` | (No tools found) |
| `LEANIX_SURVEYTOOL` | `True` | (No tools found) |
| `LEANIX_SYNCLOGTOOL` | `True` | (No tools found) |
| `LEANIX_TECHNOLOGY_DISCOVERYTOOL` | `True` | (No tools found) |
| `LEANIX_TODOTOOL` | `True` | (No tools found) |
| `LEANIX_TRANSFORMATIONSTOOL` | `True` | (No tools found) |
| `LEANIX_WEBHOOKSTOOL` | `True` | (No tools found) |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "leanix-agent": {
      "command": "leanix-agent-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "LEANIX_WORKSPACE": "${LEANIX_WORKSPACE}",
        "LEANIX_API_TOKEN": "${LEANIX_API_TOKEN}",
        "LEANIX_POLLTOOL": "${ LEANIX_POLLTOOL:-True }",
        "LEANIX_DISCOVERY_LINKING_V2TOOL": "${ LEANIX_DISCOVERY_LINKING_V2TOOL:-True }",
        "LEANIX_REFERENCE_DATA_CATALOGTOOL": "${ LEANIX_REFERENCE_DATA_CATALOGTOOL:-True }",
        "LEANIX_METRICSTOOL": "${ LEANIX_METRICSTOOL:-True }",
        "LEANIX_DISCOVERY_SAASTOOL": "${ LEANIX_DISCOVERY_SAASTOOL:-True }",
        "LEANIX_MTMTOOL": "${ LEANIX_MTMTOOL:-True }",
        "LEANIX_WEBHOOKSTOOL": "${ LEANIX_WEBHOOKSTOOL:-True }",
        "LEANIX_STORAGETOOL": "${ LEANIX_STORAGETOOL:-True }",
        "LEANIX_TRANSFORMATIONSTOOL": "${ LEANIX_TRANSFORMATIONSTOOL:-True }",
        "LEANIX_INTEGRATION_COLLIBRATOOL": "${ LEANIX_INTEGRATION_COLLIBRATOOL:-True }",
        "LEANIX_DISCOVERY_SAP_EXTENSIONTOOL": "${ LEANIX_DISCOVERY_SAP_EXTENSIONTOOL:-True }",
        "LEANIX_IMPACTSTOOL": "${ LEANIX_IMPACTSTOOL:-True }",
        "LEANIX_TECHNOLOGY_DISCOVERYTOOL": "${ LEANIX_TECHNOLOGY_DISCOVERYTOOL:-True }",
        "LEANIX_AI_INVENTORY_BUILDERTOOL": "${ LEANIX_AI_INVENTORY_BUILDERTOOL:-True }",
        "LEANIX_MANAGED_CODE_EXECUTIONTOOL": "${ LEANIX_MANAGED_CODE_EXECUTIONTOOL:-True }",
        "GRAPHQLTOOL": "${ GRAPHQLTOOL:-True }",
        "LEANIX_REFERENCE_DATATOOL": "${ LEANIX_REFERENCE_DATATOOL:-True }",
        "LEANIX_SURVEYTOOL": "${ LEANIX_SURVEYTOOL:-True }",
        "LEANIX_NAVIGATIONTOOL": "${ LEANIX_NAVIGATIONTOOL:-True }",
        "LEANIX_INTEGRATION_SIGNAVIOTOOL": "${ LEANIX_INTEGRATION_SIGNAVIOTOOL:-True }",
        "LEANIX_PATHFINDERTOOL": "${ LEANIX_PATHFINDERTOOL:-True }",
        "LEANIX_TODOTOOL": "${ LEANIX_TODOTOOL:-True }",
        "LEANIX_DISCOVERY_AI_AGENTSTOOL": "${ LEANIX_DISCOVERY_AI_AGENTSTOOL:-True }",
        "LEANIX_INTEGRATION_SERVICENOWTOOL": "${ LEANIX_INTEGRATION_SERVICENOWTOOL:-True }",
        "LEANIX_AUTOMATIONSTOOL": "${ LEANIX_AUTOMATIONSTOOL:-True }",
        "LEANIX_DISCOVERY_LINKING_V1TOOL": "${ LEANIX_DISCOVERY_LINKING_V1TOOL:-True }",
        "LEANIX_DISCOVERY_SAPTOOL": "${ LEANIX_DISCOVERY_SAPTOOL:-True }",
        "LEANIX_SYNCLOGTOOL": "${ LEANIX_SYNCLOGTOOL:-True }",
        "LEANIX_INTEGRATION_APITOOL": "${ LEANIX_INTEGRATION_APITOOL:-True }",
        "LEANIX_INVENTORY_DATA_QUALITYTOOL": "${ LEANIX_INVENTORY_DATA_QUALITYTOOL:-True }",
        "LEANIX_DOCUMENTSTOOL": "${ LEANIX_DOCUMENTSTOOL:-True }",
        "LEANIX_APPTIO_CONNECTORTOOL": "${ LEANIX_APPTIO_CONNECTORTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
leanix-agent-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only GRAPHQLTOOL enabled:

```json
{
  "mcpServers": {
    "leanix-agent": {
      "command": "leanix-agent-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "LEANIX_WORKSPACE": "${LEANIX_WORKSPACE}",
        "LEANIX_API_TOKEN": "${LEANIX_API_TOKEN}",
        "LEANIX_POLLTOOL": "False",
        "LEANIX_DISCOVERY_LINKING_V2TOOL": "False",
        "LEANIX_REFERENCE_DATA_CATALOGTOOL": "False",
        "LEANIX_METRICSTOOL": "False",
        "LEANIX_DISCOVERY_SAASTOOL": "False",
        "LEANIX_MTMTOOL": "False",
        "LEANIX_WEBHOOKSTOOL": "False",
        "LEANIX_STORAGETOOL": "False",
        "LEANIX_TRANSFORMATIONSTOOL": "False",
        "LEANIX_INTEGRATION_COLLIBRATOOL": "False",
        "LEANIX_DISCOVERY_SAP_EXTENSIONTOOL": "False",
        "LEANIX_IMPACTSTOOL": "False",
        "LEANIX_TECHNOLOGY_DISCOVERYTOOL": "False",
        "LEANIX_AI_INVENTORY_BUILDERTOOL": "False",
        "LEANIX_MANAGED_CODE_EXECUTIONTOOL": "False",
        "GRAPHQLTOOL": "True",
        "LEANIX_REFERENCE_DATATOOL": "False",
        "LEANIX_SURVEYTOOL": "False",
        "LEANIX_NAVIGATIONTOOL": "False",
        "LEANIX_INTEGRATION_SIGNAVIOTOOL": "False",
        "LEANIX_PATHFINDERTOOL": "False",
        "LEANIX_TODOTOOL": "False",
        "LEANIX_DISCOVERY_AI_AGENTSTOOL": "False",
        "LEANIX_INTEGRATION_SERVICENOWTOOL": "False",
        "LEANIX_AUTOMATIONSTOOL": "False",
        "LEANIX_DISCOVERY_LINKING_V1TOOL": "False",
        "LEANIX_DISCOVERY_SAPTOOL": "False",
        "LEANIX_SYNCLOGTOOL": "False",
        "LEANIX_INTEGRATION_APITOOL": "False",
        "LEANIX_INVENTORY_DATA_QUALITYTOOL": "False",
        "LEANIX_DOCUMENTSTOOL": "False",
        "LEANIX_APPTIO_CONNECTORTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py leanix-agent help
```

# LeanIX Agent MCP Reference

**Project:** `leanix-agent`
**Entrypoint:** `leanix-agent-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `LEANIX_WORKSPACE` | Required for authentication (e.g. https://app.leanix.net) |
| `LEANIX_API_TOKEN` | Required for API authentication |

## Available Tool Tags (2)

| Env Variable | Default |
|-------------|----------|
| `FACTSHEETSTOOL` | `True` |
| `GRAPHQLTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "leanix-agent": {
      "command": "leanix-agent-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "LEANIX_WORKSPACE": "${LEANIX_WORKSPACE}",
        "LEANIX_API_TOKEN": "${LEANIX_API_TOKEN}",
        "FACTSHEETSTOOL": "True",
        "GRAPHQLTOOL": "True"
      }
    }
  }
}
```

## Single-Tag Config Example

```json
{
  "mcpServers": {
    "leanix-agent": {
      "command": "leanix-agent-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "LEANIX_WORKSPACE": "${LEANIX_WORKSPACE}",
        "LEANIX_API_TOKEN": "${LEANIX_API_TOKEN}",
        "FACTSHEETSTOOL": "False",
        "GRAPHQLTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "leanix-agent" --tool "graphql_query" --tool-args '{"query": "query { factSheets(first:1) { edges { node { id name } } } }"}'
```

## Tailored Skills Reference

### FactSheets
Tools for interacting with LeanIX FactSheets.

- `get_factsheets(type: Optional[str] = None, page_size: Optional[int] = 40, cursor: Optional[str] = None)`: Get a list of LeanIX FactSheets.
- `get_factsheet(id: str)`: Get a specific LeanIX FactSheet by ID.

### GraphQL
Tools for using LeanIX's flexible data querying capabilities.

- `graphql_query(query: str)`: Execute a GraphQL query against LeanIX Enterprise Architecture Management.

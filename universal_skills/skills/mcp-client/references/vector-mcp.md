# Vector MCP Reference

**Project:** `vector-mcp`
**Entrypoint:** `vector-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_TYPE` | Type of database (chromadb, qdrant, milvus, etc.) |
| `DATABASE_PATH` | Path to the database files |
| `COLLECTION_NAME` | Name of the collection |
| `DOCUMENT_DIRECTORY` | Directory containing documents for indexing |

## Available Tool Tags (1)

| Env Variable | Default |
|-------------|----------|
| `VECTORTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "vector-mcp": {
      "command": "vector-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "DATABASE_TYPE": "chromadb",
        "DATABASE_PATH": "${DATABASE_PATH}",
        "COLLECTION_NAME": "memory",
        "DOCUMENT_DIRECTORY": "/documents",
        "VECTORTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
mcp-client query --server "vector-mcp" --tool "search_documents" --tool-args '{"query": "pydantic-ai"}'
```

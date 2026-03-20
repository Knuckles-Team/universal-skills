# Vector MCP Reference

**Project:** `vector-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `API_TOKEN` | Required for authentication/configuration |
| `COLLECTION_NAME` | Name of the collection |
| `DATABASE_PATH` | Path to the database files |
| `DATABASE_TYPE` | Type of database (chromadb, qdrant, milvus, etc.) |
| `DBNAME` | Required for authentication/configuration |
| `DB_HOST` | Required for authentication/configuration |
| `DB_PORT` | Required for authentication/configuration |
| `DOCUMENT_DIRECTORY` | Directory containing documents for indexing |
| `PASSWORD` | Required for authentication/configuration |
| `USERNAME` | Required for authentication/configuration |

## Available Tool Tags (3)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `COLLECTION_MANAGEMENTTOOL` | `True` | add_documents, create_collection, delete_collection, list_collections |
| `MISCTOOL` | `True` | search |
| `SEARCHTOOL` | `True` | lexical_search, semantic_search |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "vector-mcp": {
      "command": "vector-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DATABASE_TYPE": "${DATABASE_TYPE:-chromadb}",
        "DATABASE_PATH": "${DATABASE_PATH}",
        "COLLECTION_NAME": "${COLLECTION_NAME:-memory}",
        "API_TOKEN": "${API_TOKEN}",
        "DBNAME": "${DBNAME:-memory}",
        "USERNAME": "${USERNAME}",
        "PASSWORD": "${PASSWORD}",
        "DB_HOST": "${DB_HOST}",
        "DB_PORT": "${DB_PORT}",
        "DOCUMENT_DIRECTORY": "${DOCUMENT_DIRECTORY:-/documents}",
        "SEARCHTOOL": "${ SEARCHTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "COLLECTION_MANAGEMENTTOOL": "${ COLLECTION_MANAGEMENTTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
vector-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only COLLECTION_MANAGEMENTTOOL enabled:

```json
{
  "mcpServers": {
    "vector-mcp": {
      "command": "vector-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "DATABASE_TYPE": "${DATABASE_TYPE:-chromadb}",
        "DATABASE_PATH": "${DATABASE_PATH}",
        "COLLECTION_NAME": "${COLLECTION_NAME:-memory}",
        "API_TOKEN": "${API_TOKEN}",
        "DBNAME": "${DBNAME:-memory}",
        "USERNAME": "${USERNAME}",
        "PASSWORD": "${PASSWORD}",
        "DB_HOST": "${DB_HOST}",
        "DB_PORT": "${DB_PORT}",
        "DOCUMENT_DIRECTORY": "${DOCUMENT_DIRECTORY:-/documents}",
        "SEARCHTOOL": "False",
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
python mcp_client.py vector-mcp help
```

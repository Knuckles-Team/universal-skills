# Stirling PDF Agent Reference

**Mcp Client Tool Tags:** `PDFTOOL`

This agent provides an interface to the [Stirling PDF](https://docs.stirlingpdf.com/API/) tool via its REST API, allowing AI agents to manipulate PDF files.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `STIRLINGPDF_URL` | The base URL of the Stirling PDF instance | `http://localhost:8080` | No |
| `STIRLINGPDF_API_KEY` | API key if authentication is enabled | `""` | No |
| `STIRLINGPDF_VERIFY` | Whether to verify SSL certificates | `True` | No |
| `PDFTOOL` | Enable/Disable the PDF manipulation tools | `True` | No |

## Connection (stdio)

The `stirlingpdf-agent` runs over standard input/output (stdio) when spawned as a subprocess.

## Tag Workflows

### 🏷️ PDFTOOL

When `PDFTOOL=True` is set, the server exposes PDF tools including:
*   `add_watermark`: Adds a text watermark to a PDF.

#### Example MCP Client JSON

```json
{
  "mcpServers": {
    "stirlingpdf-agent": {
      "command": "stirlingpdf-agent-mcp",
      "args": [],
      "env": {
        "STIRLINGPDF_URL": "http://localhost:8080",
        "STIRLINGPDF_API_KEY": "YOUR_API_KEY",
        "PDFTOOL": "True"
      }
    }
  }
}
```

## CLI Usage

```bash
# Run the MCP server
STIRLINGPDF_URL="http://localhost:8080" stirlingpdf-agent-mcp

# Or specifically connect to testing endpoint
STIRLINGPDF_API_KEY="my-secret-key" stirlingpdf-agent-mcp
```

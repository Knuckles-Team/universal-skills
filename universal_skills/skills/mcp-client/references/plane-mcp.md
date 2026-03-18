# Plane MCP Reference

## Configuration

The reference uses the following environment variables:

- `PLANE_API_KEY`: Your Plane API Key.
- `PLANE_WORKSPACE_SLUG`: Your Plane Workspace Slug.
- `PLANE_BASE_URL`: The base URL for your Plane instance (defaults to `https://api.plane.so`).

## MCP Configuration

```json
{
  "mcpServers": {
    "plane": {
      "command": "uvx",
      "args": ["plane-mcp-server", "stdio"],
      "env": {
        "PLANE_API_KEY": "<your-api-key>",
        "PLANE_WORKSPACE_SLUG": "<your-workspace-slug>",
        "PLANE_BASE_URL": "https://api.plane.so"
      }
    }
  }
}
```

## Usage

```bash
# Example CLI usage via mcp-client
python -m universal_skills.skills.mcp_client.run_mcp_tool plane list-projects
```

# GitHub MCP Reference

This reference allows the agent to interact with GitHub using the official GitHub Copilot MCP server.

## Configuration

The reference uses the following environment variables:

- `GITHUB_PAT`: Your GitHub Personal Access Token.

## MCP Configuration

```text
server: github
url: https://api.githubcopilot.com/mcp/
headers:
  Authorization: Bearer YOUR_GITHUB_PAT
```

Register this command and environment in the server list of the MCP client in use.

## Usage

```bash
# Example CLI usage via mcp-client
python -m universal_skills.skills.mcp_client.run_mcp_tool github get_repository owner=octocat repo=hello-world
```

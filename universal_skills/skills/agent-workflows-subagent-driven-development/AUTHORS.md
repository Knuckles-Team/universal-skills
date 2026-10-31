# A2A Orchestrator - Agent Registry

This skill registers A2A agents and exposes them for orchestration via `sessions_spawn`.

## Agent Registry

Keep the registry for your deployment in your own configuration. Each entry maps a deployment name to its A2A endpoint and the MCP servers it uses.

| Deployment | Agent URL | MCP URL(s) | Status |
|------------|-----------|------------|--------|
| `<name>-agent` | `https://<name>-agent.example.com/a2a` | `https://<name>-mcp.example.com` | Deployed, WIP, or Not deployed |

## Usage

Spawn any agent by name:

```ts
sessions_spawn(agentId="<name>-agent", task="list containers")
```

For per-node agents, specify the node suffix in the agent name:

```ts
sessions_spawn(agentId="<name>-agent-<node>", task="inspect the node")
```

## Notes

- A private DNS zone may require VPN or local network access.
- WIP/Not Deployed agents will fail spawn — handle gracefully.

---

Built for OpenClaw. Maintained by Crawdaunt.

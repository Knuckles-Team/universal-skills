# A2A Orchestrator - Homelab Agents

This skill registers all homelab A2A agents and exposes them for orchestration via `sessions_spawn`.

## Agent Registry

| Deployment | Agent URL(s) | MCP URL(s) | Status |
|------------|--------------|------------|--------|
| homelab-genius-agent | genius-agent.arpa/a2a | archivebox-mcp.arpa | WIP, not deployed |
| homelab-adguard-home-agent | adguard-agent.arpa/a2a | adguard-mcp.arpa | Deployed |
| homelab-arr-stack-agent | arr-agent.arpa/a2a | chaptarr-mcp.arpa, lidarr-mcp.arpa, prowlarr-mcp.arpa, radarr-mcp.arpa, sonarr-mcp.arpa, bazarr-mcp.arpa, seerr-mcp.arpa, arr-mcp.arpa | Deployed |
| homelab-archivebox-agent | archivebox-agent.arpa/a2a | archivebox-mcp.arpa | Deployed |
| homelab-audio-transcriber-agent | audio-transcriber-agent.arpa/a2a | audio-transcriber-mcp.arpa | WIP |
| homelab-container-manager-agent (6 nodes) | container-manager-agent-*.arpa/a2a | container-manager-*.arpa | Deployed |
| homelab-documentdb-agent | documentdb-agent.arpa/a2a | documentdb-mcp.arpa | Not deployed |
| homelab-github-agent | github-agent.arpa/a2a | github-mcp.arpa | WIP |
| homelab-gitlab-agent | gitlab-agent.arpa/a2a | gitlab-mcp.arpa | Deployed |
| homelab-jellyfin-agent | jellyfin-agent.arpa/a2a | jellyfin-mcp.arpa | Deployed |
| homelab-mealie-agent | mealie-agent.arpa/a2a | mealie-mcp.arpa | WIP |
| homelab-media-downloader-agent | media-downloader-agent.arpa/a2a | media-downloader-mcp.arpa | Deployed |
| homelab-microsoft-agent | microsoft-agent.arpa/a2a | microsoft-mcp.arpa | WIP |
| homelab-nextcloud-agent | nextcloud-agent.arpa/a2a | nextcloud-mcp.arpa | Deployed |
| homelab-openclaw-agent | openclaw-agent.arpa/a2a | — | Not deployed |
| homelab-repository-manager-agent | repository-manager-agent.arpa/a2a | repository-manager-mcp.arpa | Deployed |
| homelab-searxng-agent | searxng-agent.arpa/a2a | searxng-mcp.arpa | Deployed |
| homelab-servicenow-agent | servicenow-agent.arpa/a2a | servicenow-mcp.arpa | Deployed |
| homelab-systems-manager-agent (6 nodes) | systems-manager-agent-*.arpa/a2a | systems-manager-*.arpa | Deployed |
| homelab-tunnel-manager-agent | tunnel-manager-agent.arpa/a2a | tunnel-manager-mcp.arpa | Deployed |
| homelab-vector-agent | vector-agent.arpa/a2a | vector-mcp.arpa | RAG memory agent |

## Usage

Spawn any agent by name:

```ts
sessions_spawn(agentId="homelab-container-manager", task="list containers")
```

For per-node agents, specify the node suffix in the task:

```ts
sessions_spawn(agentId="homelab-container-manager-agent-gr1080", task="inspect container-manager-gr1080.arpa")
```

## Notes

- Internal `.arpa` DNS requires VPN or local network access.
- WIP/Not Deployed agents will fail spawn — handle gracefully.

---

Built for OpenClaw. Maintained by Crawdaunt.

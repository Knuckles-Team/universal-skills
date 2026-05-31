---
name: caddy-uptime-sync
description: >-
  Synchronizes DNS entries from Caddy to Uptime Kuma monitors. Use when the user asks to sync Caddy domains to Uptime Kuma, add missing caddy entries to uptime kuma, or compare Caddy config with Uptime Kuma.
license: MIT
tags: [caddy, uptime-kuma, sync, monitors, networking, ops]
metadata:
  author: Genius
  version: '0.1.21'
---
# Caddy to Uptime Kuma Sync

This skill orchestrates the synchronization of domain entries from a Caddy configuration into Uptime Kuma monitors.

## Workflow

1. **Retrieve Caddy Configuration**
   - Connect to the Caddy MCP server (typically `caddy-mcp`).
   - Use the available Caddy MCP tools (e.g., `get_config` or `get_routes`) to extract the current Caddy configuration.
   - Parse the configuration to compile a comprehensive list of all configured domain names (host matchers or upstream servers).

2. **Retrieve Uptime Kuma Monitors**
   - Connect to the Uptime Kuma MCP server (typically `uptime-kuma-mcp` or `uptime-mcp`).
   - Use the available Uptime Kuma MCP tools to fetch the list of all currently configured monitors.
   - Extract the URLs or domains being monitored by Uptime Kuma.

3. **Compare and Identify Deltas**
   - Identify domains present in Caddy but **missing** from Uptime Kuma.
   - Identify domains present in Uptime Kuma but **missing** from Caddy.

4. **Request User Confirmation**
   - Present a clearly formatted Markdown list to the user showing:
     - **To be added to Uptime Kuma**: [List of domains]
     - **Missing from Caddy (potentially to be removed from Uptime Kuma)**: [List of domains]
   - **WAIT** for the user's explicit confirmation before making any modifications. Ask the user if they want to add the missing items, remove the orphaned items, or both.

5. **Execute Synchronization**
   - Ask the user for their preferred default monitor interval and any other specific Uptime Kuma settings they would like applied to the new monitors.
   - Upon receiving user approval, use the Uptime Kuma MCP tools to create new monitors for the approved domains.
   - Infer whether the site is HTTP or HTTPS based directly on the Caddy configuration (e.g., if it has TLS configured or is explicitly listening on a secure port). Do NOT blindly assume HTTPS.
   - If the user approved removing orphaned monitors, use the appropriate Uptime Kuma tool to delete them.
   - Provide a final summary of the operations completed.

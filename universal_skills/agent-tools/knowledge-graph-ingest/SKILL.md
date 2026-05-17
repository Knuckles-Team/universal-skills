---
name: knowledge-graph-ingest
description: >-
  Bulk ingests the workspace projects, ScholarX documents, and conversation logs into the Knowledge Graph.
  Use when the user wants to "ingest the workspace", "bulk ingest", "ingest these git urls",
  "ingest conversations", "backup the kg", or "wipe the kg".
  Automatically handles finding all workspace paths natively via the repository-manager MCP,
  cloning parallel git URLs if requested, and firing off the ingestion pipeline.
license: MIT
tags: [knowledge-graph, ingestion, workspace, bulk, git, conversations, backup]
metadata:
  author: Genius
  version: '2.0.0'
---

# Knowledge Graph Ingestion

This skill coordinates bulk data ingestion into the unified Knowledge Graph. It handles retrieving workspace configuration, cloning ad-hoc repositories, ingesting conversation logs from multiple IDEs/agents, and triggering the ingestion pipeline.

## Capabilities

### 1. Default Workspace & ScholarX Ingestion
When the user asks to ingest the workspace (without specifying explicit targets), you MUST:
1. Get the local workspace paths by executing the `mcp_repository-manager_rm_workspace` tool with `action: 'paths'`. This natively returns a list of all absolute paths for projects defined in the ecosystem.
2. Append the default ScholarX document directory to the list: `~/.local/share/scholarx/papers`
3. Convert the combined list of paths into a JSON-formatted array.
4. Execute the `mcp_agent-utilities-kg_kg_ingest` tool, passing the JSON array to the `target_path` parameter.

### 2. Parallel Git URL Cloning
If the user specifies explicit comma-separated Git URLs to ingest:
1. You MUST clone them locally in parallel before ingestion.
2. Use your `run_command` tool to execute a bash script that clones all URLs simultaneously into `/home/apps/workspace/open-source-libraries/` (or another appropriate directory).
   - **Example:** `git clone <url1> & git clone <url2> & wait`
3. After the clones complete, compile the local absolute paths of the cloned directories into a JSON array.
4. Execute `mcp_agent-utilities-kg_kg_ingest` with the JSON array.

### 3. Conversation Log Ingestion
Ingest conversation logs from supported IDE/agent platforms:
- **Antigravity**: `~/.gemini/antigravity/brain/*/overview.txt`
- **Windsurf**: `~/.codeium/windsurf/memories/` or `~/.windsurf/memories/`
- **Claude Code**: `~/.claude/projects/` or `~/.config/claude/`
- **Codex**: `~/.codex/sessions/`

To ingest conversations, call `mcp_agent-utilities-kg_kg_ingest` with the conversation log directories as targets.
Conversation logs are ingested as `Conversation` nodes with `DISCUSSED_IN` edges linking to relevant Concept nodes.

### 4. DB Backup & Wipe
- **Backup**: `mcp_agent-utilities-kg_kg_inspect` with `view: 'backup'` — creates a timestamped backup of the database.
- **Wipe**: `mcp_agent-utilities-kg_kg_inspect` with `view: 'wipe'` — clears all nodes and edges for a fresh start.

### 5. Progress Monitoring
After triggering the ingestion, you should:
1. Call `mcp_agent-utilities-kg_kg_jobs` with `action: 'list'` to monitor the ingestion queue.
2. Report the completion percentage and job status to the user.

### 6. ScholarX Paper Downloads & Ingestion
When the user asks to download or ingest a research paper using the ScholarX MCP tools, and they provide only a raw numerical or alphanumeric ID (e.g., `2605.12975`):
1. You MUST explicitly prompt the user to confirm the paper's source (e.g., "Is this from arXiv, PMC, bioRxiv, etc.?").
2. Once the user confirms the source, you MUST prepend the source prefix to the ID (e.g., `arxiv:2605.12975`) before executing the `sx_search` or `sx_storage` tools.
3. After the paper is downloaded, you can ingest it by executing `mcp_agent-utilities-kg_kg_ingest` with the local downloaded file path as the `target_path`.

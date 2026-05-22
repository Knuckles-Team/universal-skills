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
5. **Prompt for Chat Ingestion**: Explicitly prompt the user to confirm whether they would like to ingest all conversation/chat logs from active IDE platforms (e.g. Antigravity or Claude Code) to capture development history and context.
6. **Tool/Skill Configuration Hydration**: Incorporate the IDE's/global active `mcp_config.json` (e.g., at `~/.config/agent-utilities/mcp_config.json`) and the agent skills directories (defaulting to `/home/apps/workspace/agent-packages/skills/universal-skills` and `/home/apps/workspace/agent-packages/skills/skill-graphs`) as ingestion targets to ensure the Knowledge Graph is fully hydrated with active tool, schema, and capability definitions.

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

When the user consents to or requests conversation ingestion, you MUST identify all existing logs from these directories, compile them into a target list, and call `mcp_agent-utilities-kg_kg_ingest` with the log directories/files.
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

### 7. Infrastructure Topology Ingestion (CONCEPT:OS-5.3)
When ingesting the workspace, you MUST also ingest infrastructure state to fully
hydrate the Knowledge Graph with the physical and virtual topology:

#### 7a. Inventory File
Ingest `~/.config/agent-utilities/inventory.yaml` as the canonical hardware inventory.
For each host entry, create or update a `HardwareNode` KG node with:
- `hostname`, `ip_address` (from `ansible_host`), `group`, `status`
- `ssh_user` (from `ansible_user`), `ssh_key` (from `ansible_ssh_private_key_file`)
- Any extended metadata (`hardware.*`, `os.*`, `roles`, `containers.*`, `networking.*`)

Create `HAS_INTERFACE` edges from `HardwareNode` → `NetworkInterface` nodes for each
network interface defined, and `CONNECTS_VIA` edges for any VPN tunnel entries.

#### 7b. Ontology Files
Include all OWL ontology files as ingestion targets:
- `agent_utilities/knowledge_graph/ontology.ttl` — base ontology
- `agent_utilities/knowledge_graph/ontology_infrastructure.ttl` — infrastructure module

These provide the formal BFO-aligned class hierarchy for all infrastructure nodes.

#### 7c. Workflow Catalog
Ingest `agent_utilities/workflows/catalog.yaml` to create `WorkflowDefinition` nodes
for each workflow, with `HAS_STEP` edges to individual `WorkflowStep` nodes and
`REQUIRES_TOOL` edges to the MCP server `CallableResource` nodes they reference.

#### 7d. Topology Snapshots
If topology maps exist at `~/.local/share/agent-utilities/topology/`, ingest them:
- `topology.json` — full infrastructure graph snapshot
- `service_map.json` — service dependency chains
- `network_map.json` — network topology

These create/update `Container`, `ContainerStack`, `NetworkSubnet`, `DNSRewrite`,
`ReverseProxy`, and `ObservabilityStack` nodes with their respective edges
(`RUNS_ON`, `BELONGS_TO_STACK`, `DEPLOYED_ON`, `ROUTES_TO`, `RESOLVES_DNS_FOR`, etc.).

#### 7e. DNS Rewrites
Query `adguard-home-mcp` → `list_rewrites` and ingest each rewrite as a `DNSRewrite`
node with `RESOLVES_DNS_FOR` edges linking to the corresponding `PlatformService` node.

#### 7f. Container State (Live)
If `container-manager-mcp` or `portainer-mcp` are available, query live container
and stack state and ingest as `Container` and `ContainerStack` nodes with `RUNS_ON`
and `BELONGS_TO_STACK` edges to the appropriate `HardwareNode` nodes.

#### Default Ingestion Target List
When performing a full workspace ingestion, the following infrastructure paths
MUST be appended to the ingestion target list:
```
~/.config/agent-utilities/inventory.yaml
~/.config/agent-utilities/mcp_config.json
~/.config/agent-utilities/config.json
~/.local/share/agent-utilities/topology/
agent_utilities/knowledge_graph/ontology.ttl
agent_utilities/knowledge_graph/ontology_infrastructure.ttl
agent_utilities/workflows/catalog.yaml
```

---
name: agent-builder
description: Guide for building scalable Pydantic AI agents. Use this skill when the user wants to create a new agent package or modify an existing agent's architecture, to ensure it follows the standardized agent patterns using `agent-utilities`.
license: MIT
tags: [agent, development, pydantic-ai, architecture]
metadata:
  author: Audel Rouhi
  version: '0.1.49'
---
# Agent Builder Guide

This skill provides guidelines and templates for building Pydantic AI agents that adhere to our standardized architecture using the `agent-utilities` package.

## Architecture: Agent Pattern

When building a new agent, you must use the **Agent Pattern**. Agent will have access to all authorized capabilities via the `mcp-client` universal skill.

**Reference:** `reference/agent_template.md` contains the required boilerplate.

---

## Implementation Workflow

Follow these steps when defining a new agent package:

### 1. Initialize the Package
1. Create a `my_agent/agent_data` directory within the package.
2. Ensure `pyproject.toml` depends on `agent-utilities>=0.2.23` (and includes `agent` under optional dependencies).
3. Configure `project.scripts` in `pyproject.toml` to expose the agent entry point (e.g., `my-agent = "my_package.agent_server:agent_server"`).

### 2. Configure Agent Workspace Files
The agent's behavior and state are controlled by several core files in the `agent_data/` directory:

- **IDENTITY.md**: Injects the agent's name, role, system prompt, and tools instructions. Use a single `[default]` block containing the metadata and prompt. (See `reference/agent_template.md`).
- **USER.md**: Information about the user (name, style, preferences).
- **A2A_AGENTS.md**: Registry of known A2A peer agents.
- **MEMORY.md**: Long-term memory and event logs.
- **CRON.md**: Persistent scheduled tasks.
- **CRON_LOG.md**: History of execution for scheduled tasks.
- **HEARTBEAT.md**: Periodic self-check tasks and instructions.
- **chats/**: (Directory) Persistent storage for background job conversations.
- **mcp_config.json**: Configuration for MCP servers.
- **icon.png**: Visual representation of the agent.

Each file plays a critical role in how the agent operates and interacts within the workspace.

### 3. Implement the Agent Entry Point (`agent_server.py`)
Create `agent_server.py` in the package source directory (NOT in `agent_data`).
Use `load_identity()` to fetch the `[default]` metadata. Capture the environmental default variables (including OTel, host, port, mcp config, and A2A configurations) and pass them to `create_agent_server()`.
Ensure you extract the appropriate arguments from `create_agent_parser` to pass to `create_agent_server`, including:
- `otel_endpoint`, `otel_headers`, `otel_public_key`, `otel_secret_key`, `otel_protocol`
- `a2a_broker`, `a2a_broker_url`, `a2a_storage`, `a2a_storage_url`

### 4. System Prompt and Context
When initializing the `Agent`, ensure the system prompt is built dynamically. Using `build_system_prompt_from_workspace()` is the recommended approach to ensure all core context files (`IDENTITY.md`, `USER.md`, `A2A_AGENTS.md`, `MEMORY.md`, `CRON.md`, `CRON_LOG.md`, `HEARTBEAT.md`, etc.) are combined into a rich prompt.

### 4. Verification
After implementation:
- Verify the agent starts correctly by running `python -m my_package.agent --help`.
- Run `run_pre_commits.sh` (or `pre-commit run --all-files`) in the workspace to ensure styling and syntax compliance.

## Reference Documents

The following references are provided alongside this skill:
- [Agent Boilerplate](reference/agent_template.md)

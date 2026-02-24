---
name: agent-builder
description: Guide for building scalable Pydantic AI agents operating either as a single agent or a multi-agent system. Use this skill when the user wants to create a new agent package or modify an existing agent's architecture, to ensure it follows the standardized agent patterns using `agent-utilities`.
categories: [Development]
tags: [agent, development, pydantic-ai, multi-agent, architecture]
---

# Agent Builder Guide

This skill provides guidelines and templates for building Pydantic AI agents that adhere to our standardized architecture using the `agent-utilities` package.

## Architecture Selection: Single vs. Multi-Agent

When building a new agent, you must first choose the appropriate architectural pattern based on the number of MCP tools and the complexity of the domain.

### Single-Agent Pattern
**When to choose:** Select this pattern when the agent only interacts with a handful of tools (e.g., `< 10`) within a single, cohesive domain.
**Why:** It is simpler to manage and the single agent's context window can easily handle the smaller set of tools without getting confused or hitting context limits.
**Example:** `searxng-mcp`, which manages a small set of web search tools via a single agent.
**Reference:** `reference/single_agent_template.md` contains the required boilerplate.

### Multi-Agent Pattern
**When to choose:** Select this pattern when interacting with a large number of MCP tools, or across distinct domains requiring differing capabilities.
**Why:** Tools are distributed across specialized child agents (sub-agents) by their MCP tool tag category. A supervisor agent routes requests to the appropriate child agent. This keeps the context window of each individual agent small, improving reliability and reasoning performance.
**Example:** `servicenow-api`, which routes requests to specialized agents like `[cmdb]`, `[incidents]`, `[hr]`, etc.
**Reference:** `reference/multi_agent_template.md` contains the required boilerplate.

---

## Implementation Workflow

Follow these steps when defining a new agent package:

### 1. Initialize the Package
1. Create a `my_agent/agent` directory within the package.
2. Ensure `pyproject.toml` depends on `agent-utilities>=0.1.7` (and includes `agent` under optional dependencies).
3. Configure `project.scripts` in `pyproject.toml` to expose the agent entry point (e.g., `my-agent = "my_package.agent:agent_server"`).

### 2. Configure Agent Identity (`IDENTITY.md`)
Create an `IDENTITY.md` file in the `agent/` directory. This file injects the agent's name, role, system prompt, and tools instructions.

- **Single-Agent:** Use a single `[default]` block containing the metadata and prompt. (See `reference/single_agent_template.md`).
- **Multi-Agent:** Define a `[supervisor]` block for the main router agent, followed by individual blocks for each child agent (e.g., `[cmdb]`, `[incidents]`). (See `reference/multi_agent_template.md`).

### 3. Implement the Agent Entry Point (`agent.py`)
Create `agent.py` in the `agent/` directory.

- **For Single-Agents:** Use `load_identity()` to fetch the `[default]` metadata and pass it to `create_agent_server()`.
- **For Multi-Agents:** Use `load_identities()` to fetch all blocks. Extract the `supervisor` for the main agent, and use dictionary comprehension to map the remaining identities to `CHILD_AGENT_DEFS`, which are passed as the `agent_definitions` parameter to `create_agent_server()`.

### 4. Verification
After implementation:
- Verify the agent starts correctly by running `python -m my_package.agent --help`.
- Run `run_pre_commits.sh` (or `pre-commit run --all-files`) in the workspace to ensure styling and syntax compliance.

## Reference Documents

The following references are provided alongside this skill:
- [Single Agent Boilerplate](reference/single_agent_template.md)
- [Multi Agent Boilerplate](reference/multi_agent_template.md)

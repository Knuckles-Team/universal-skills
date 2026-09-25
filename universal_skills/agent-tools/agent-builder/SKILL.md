---
name: agent-builder
domain: agent-tools
skill_type: skill
description: >-
  How an agent experience is provided for a connector or package in the GraphOS
  ecosystem. Use this skill when the user wants to "create an agent" for a
  connector, add an agent entry point to an agent package, or migrate an
  existing per-connector agent. Per-connector standalone agents
  (agent_server.py plus a <name>-agent console script) are retired: graph-os and
  agent-utilities compose the agent over the connector's MCP tools, and the
  connector ships only its MCP server and its content (prompt, skills,
  ontology) through agent-connector-sdk.
license: MIT
tags: [agent, development, pydantic-ai, architecture, connectors]
metadata:
  version: '1.3.1'
  author: Genius
---
# Agent Builder Guide

## The rule

**Do not create a per-connector agent.** No `agent_server.py`, no `<name>-agent`
console script, no `agent` optional-dependency extra, no `create_agent_server()` call in
a connector package. That pattern is retired fleet-wide.

The "chat with this connector" experience is served by **graph-os**, which asks
**agent-utilities** (the agent orchestration plane) to compose an agent over the
connector's MCP tools. A connector contributes only:

- its **MCP server**, built with `agent-connector-sdk` (see `mcp-builder`);
- its **content** — the structured system prompt (`prompt-builder`), skills, and
  ontology/shapes — published as a pack certified by `agent-connector-sdk` and
  committed to epistemic-graph.

## Migrating a package that still has an agent entry point

1. Delete `<pkg>/agent_server.py` and any `__main__`/CLI path that only launched it.
2. Remove its console script from `[project.scripts]` and the `agent` extra (with any
   dependency only it needed) from `pyproject.toml`; regenerate `uv.lock` once.
3. Keep the structured prompt as connector content so the composed agent still
   receives it; remove agent-runtime imports (`create_agent_server`,
   `create_agent_parser`, `load_identity`) from the package.
4. Remove the agent entry from the package's README, `mcp_config*.json`, compose files
   and docs in the same change; no alias or deprecated entry point stays behind.
5. Run the package's targeted tests and its hooks on the changed files.

## Where agent behaviour is built instead

Agent graphs, planning, delegation, harness adapters and model profiles live in
agent-utilities (`agent-utilities-development`); serving and the "chat with a
connector" surface live in graph-os (`graph-os-development`). Shared rules:
`graphos-ecosystem-development`.

---
name: agent-spawner
domain: agent-tools
skill_type: skill
description: >-
  Run one isolated delegated agent from the AgentConfig model, MCP, TLS, and
  skills catalogs. Use when a bounded task needs a temporary specialist without
  mutating the parent agent; prefer GraphOS delegation for graph-governed work.
tags: [agent, delegation, graph-os, pydantic-ai, orchestration]
license: MIT
metadata:
  version: '1.2.1'
  author: Repository Maintainers
---

# Agent Spawner

Run one temporary isolated agent using deployment-neutral `AgentConfig`:

```bash
python scripts/spawn_agent.py --prompt "Inspect the configured tool catalog"
```

`CHAT_MODELS`, `MCP_CONFIG`, `MCP_URL`, the custom-skills root, TLS policy, and
runtime secret resolution come from AgentConfig/XDG configuration. Provider and
model identifiers may be selected explicitly when they already exist in the
deployment's model catalog:

```bash
python scripts/spawn_agent.py \
  --provider openai \
  --model-id configured-model \
  --prompt "Perform the bounded delegated task"
```

The compatibility flags that accepted API keys, arbitrary dotenv/config paths,
base URLs, personal agent names, or disabled TLS verification are retired.
Never put credentials in arguments. The child uses strict tool guards and MCP
isolation, emits no prompt/name/path/endpoint details, and relies on the shared
transport profile. Use GraphOS delegation when policy, capability provenance,
or trace-linked skill execution is required.

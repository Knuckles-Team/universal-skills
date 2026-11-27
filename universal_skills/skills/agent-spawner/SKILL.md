---
name: agent-spawner
domain: agent-tools
skill_type: skill
description: >-
  Run one isolated delegated agent from the AgentConfig model, MCP, TLS, and
  skills catalogs. Use when a bounded task needs a temporary specialist without
  mutating the parent agent; prefer Arbora delegation for graph-governed work.
tags: [agent, delegation, arbora, pydantic-ai, orchestration]
license: MIT
metadata:
  version: '1.7.0'
  author: Knuckles-Team
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
transport profile. Use Arbora delegation when policy, capability provenance,
or trace-linked skill execution is required.

## Steps

1. Confirm the AgentConfig catalogs resolve by running `python scripts/spawn_agent.py --help`. Verify that usage prints with `--prompt`, `--provider` and `--model-id` options.
2. Write a bounded prompt and run `python scripts/spawn_agent.py --prompt "<bounded task>"`. Verify that the child exits 0 and prints a result.
3. If a specific model is needed, run `python scripts/spawn_agent.py --provider <provider> --model-id <id> --prompt "<task>"` using an id from the deployment catalog. Verify that the run does not report an unknown model.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Unknown provider or model error | `--model-id` is not in the `CHAT_MODELS` catalog | Pick an id that exists in the AgentConfig catalog, or omit the flags to use the default. |
| Unrecognized argument error | Retired flags such as API keys, base URLs or dotenv paths were passed | Remove them and configure credentials and endpoints through AgentConfig and XDG configuration. |
| No MCP tools available to the child | `MCP_CONFIG` or `MCP_URL` not set in AgentConfig | Set them in the AgentConfig configuration and re-run. |

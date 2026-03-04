---
name: agent-spawner
description:
  Spawns a new Pydantic AI agent dynamically using an MCP configuration and interacts with it using a prompt.
  Use when an agent needs to dynamically instantiate a sub-agent with a fresh configuration.
license: MIT
tags: [agent, sub-agent, mcp, dynamic, spawner, pydantic-ai, orchestration]
metadata:
  author: Audel Rouhi
  version: '0.1.21'
---
# Agent Spawner Skill

The `agent-spawner` skill provides the ability to dynamically create a new Pydantic AI agent configured with an external MCP server toolkit. This is extremely useful when an agent wants to spin up a sub-agent with specialized tools defined in an `mcp_config.json`, and interact with that agent immediately without modifying the parent agent's state or toolset.

## Usage

This skill includes a CLI script `spawn_agent.py` that utilizes `agent_utilities.create_agent` to build the agent and `agent_utilities.chat` to send it a prompt and wait for the response.

To use the tool, execute the script with the required arguments.

### Examples

**Spawning an Agent with a single Prompt:**

```bash
python -m universal_skills.skills.agent-spawner.scripts.spawn_agent \
    --mcp-config ./references/example_mcp_config.json \
    --prompt "What tools are available to you?"
```

**Spawning an Agent with a specific Name and System Prompt:**

```bash
python -m universal_skills.skills.agent-spawner.scripts.spawn_agent \
    --mcp-config ./references/example_mcp_config.json \
    --prompt "Please execute a scan" \
    --name "SecurityScanner" \
    --system-prompt "You are a security scanning agent. Always use available tools."
```

## Arguments

- `--prompt`: (Required) The instruction/prompt to send to the newly spawned agent.
- `--mcp-config`: Path to the `mcp_config.json` file configuring the capabilities. (Defaults to `MCP_CONFIG` env).
- `--mcp-url`: Alternative to config, a URL directly to a single MCP server. (Defaults to `MCP_URL` env).
- `--custom-skills-directory`: Path to directory to load custom Universal Skills. (Defaults to `CUSTOM_SKILLS_DIRECTORY` env).
- `--name`: The name of the spawned agent. (Defaults to `DEFAULT_AGENT_NAME` env).
- `--system-prompt`: The system prompt to apply. (Defaults to `AGENT_SYSTEM_PROMPT` env).
- `--provider`: The LLM Provider to use inside the agent (e.g. `openai`, `anthropic`). (Defaults to `PROVIDER` env).
- `--model-id`: The model identifier. (Defaults to `MODEL_ID` env).
- `--base-url`: LLM Base URL for API calls. (Defaults to `LLM_BASE_URL` env).
- `--api-key`: API key for the LLM. (Defaults to `LLM_API_KEY` env).
- `--insecure`: Disable SSL verification for MCP and LLM calls.

## Implementation Details

The script depends on `agent_utilities` which must be installed in the environment. It loads the MCP servers defined in the config file, instantiates a Pydantic AI agent with those MCP servers, and uses the `chat` method to dispatch the user's prompt to the newly formed agent.

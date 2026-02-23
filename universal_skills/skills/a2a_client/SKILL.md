---
name: a2a-client
description: Communicate with other agents using the Agent-to-Agent (A2A) protocol.
categories: [Core]
tags: [agent, protocol, network]
---

# A2A Client

## Overview
This skill allows the agent to act as a client and communicate with other A2A-compatible agents. It handles agent discovery (via `agent-card.json`), message sending (via JSON-RPC), and result polling.

## Capabilities/Tools
- **Agent Discovery**: Validates the target agent by fetching its `.well-known/agent-card.json`.
- **Send Message**: Sends a prompt/query to the target agent to initiate a task.
- **Poll Results**: Monitors the task status and retrieves the final response when complete.

## Resources
### scripts/
- `scripts/a2a_client.py`: The core python script that implements the A2A client logic.

## Usage
Run the script `scripts/a2a_client.py` with either the target agent's explicitly provided URL or the target agent's Name as defined in your local `AGENTS.md` file, along with your query.

**Arguments:**
- `--url`: (Optional unless `--agent-name` is omitted) The base URL of the A2A endpoint (e.g., `http://target-agent.arpa/a2a/`).
- `--agent-name`: (Optional unless `--url` is omitted) The name of the target agent to automatically look up in the local `AGENTS.md` file.
- `--agents-file`: (Optional) Path to the `AGENTS.md` file. Defaults to `agent/AGENTS.md` which is standard.
- `--query`: The text message or query you want to send to the agent.

## Example
To ask a search agent (named SearchMaster in your `AGENTS.md`) about the latest news about the United States:
```bash
python3 genius_agent/skills/a2a_client/scripts/a2a_client.py \
  --agent-name SearchMaster \
  --query "Can you search the latest news about the United States?"
```

Alternatively, direct URL fallback:
```bash
python3 genius_agent/skills/a2a_client/scripts/a2a_client.py \
  --url http://searxng-agent.arpa/a2a/ \
  --query "Can you search the latest news about the United States?"
```

## Protocol Flow
1.  **Validation**: `GET {url}/.well-known/agent-card.json`
2.  **Send Message**: `POST {url}` with JSON-RPC method `message/send`
3.  **Poll Status**: `POST {url}` with JSON-RPC method `tasks/get` until state is `completed` (or failed).

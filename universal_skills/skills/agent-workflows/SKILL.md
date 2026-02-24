---
name: agent-workflows
description: "Consolidated skill for managing, dispatching, and orchestrating other agents via the agent-manager CLI, as well as workflows for A2A communication, orchestration, and parallel subagent dispatch."
categories: [Core, Productivity]
tags: [agents, a2a, subagents, multi-agent, parallel, orchestration, manager, protocol, network]
---

# Agent Workflows & Orchestration

## Overview
This skill consolidates tools and methodologies for managing agents, dispatching subagents, and direct Agent-to-Agent (A2A) communication via JSON-RPC.

## Capabilities/Tools

### 1. Agent Manager CLI (`scripts/main.py`)
This script enables controlling other independent agents running in the ecosystem. It manages runtimes, heartbeats, states, and lifecycles.

```bash
# List all running agents
python scripts/main.py list

# Start an agent heartbeat
python scripts/main.py heartbeat start <agent_name>

# Check the status of agent runtimes
python scripts/main.py status

# Schedule a task to run periodically
python scripts/main.py schedule <agent_name> "cron_expression"
```

### 2. A2A Client (`scripts/a2a_client.py`)
This tool allows the agent to act as a client and communicate with other A2A-compatible agents. It handles agent discovery (`agent-card.json`), message sending (JSON-RPC), and result polling.

**Usage:**
Run the script with the target agent's explicitly provided URL or the target agent's Name (from `AGENTS.md`), along with your query.

```bash
# Ask a search agent (SearchMaster) to search the web
python scripts/a2a_client.py \
  --agent-name SearchMaster \
  --query "Can you search the latest news about the United States?"

# Alternatively, direct URL fallback:
python scripts/a2a_client.py \
  --url http://searxng-agent.arpa/a2a/ \
  --query "Can you search the latest news about the United States?"
```

## Workflows

### 3. A2A & Subagent Methodologies (`docs/`)
Follow the patterns outlined in the `docs/` folder when designing workflows that involve spawning independent agent worker nodes:
- **A2A Orchestration**: Use explicit protocol interfaces when communicating between isolated AI agents. Ensure one agent serves as the coordinator while others act as execution workers.
- **Dispatching Parallel Agents**: Don't force one agent to do multiple isolated tasks sequentially. Spin up multiple isolated environments (or TMUX sessions) and invoke worker routines in parallel for faster results.
- **Subagent-Driven Development**: During complex execution tasks, break down the work into discrete chunks and farm it out to specialized subagents. You are the supervisor; they are the workers. Ensure they have clear constraints and output expected artifacts that you can subsequently review.

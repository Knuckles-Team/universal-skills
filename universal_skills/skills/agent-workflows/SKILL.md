---
name: agent-workflows
description: Consolidated skill for managing, dispatching, and orchestrating other agents via the agent-manager CLI, as well as workflows for A2A communication, orchestration, and parallel subagent dispatch.
license: MIT
tags: [agents, a2a, subagents, multi-agent, parallel, orchestration, manager, protocol, network]
metadata:
  author: Audel Rouhi
  version: '0.1.29'
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
This tool allows the agent to act as a client and communicate with other A2A-compatible agents. It handles agent discovery (`agent-card.json`), message sending (JSON-RPC), task queue monitoring, and result polling or streaming (SSE).

**Usage:**
Run the script with the target agent's explicitly provided URL or the target agent's Name (from `AGENTS.md`), along with your query and the desired action.

**Available Actions:**
- `chat` (default): Send a message and wait for the result.
- `get-card`: Retrieve and display the agent's full capability card.
- `list-tasks`: Monitor the agent's active task queue.

**Examples:**
```bash
# 1. Ask an agent to search the web (polling)
python scripts/a2a_client.py \
  --agent-name SearchMaster \
  --action chat \
  --query "Can you search the latest news about the United States?"

# 2. Ask an agent and stream real-time updates (SSE)
python scripts/a2a_client.py \
  --url http://searxng-agent.arpa/a2a/ \
  --action chat \
  --stream \
  --query "Explain quantum mechanics in 1 line."

# 3. View the Agent Card capabilities
python scripts/a2a_client.py --agent-name SearchMaster --action get-card

# 4. Monitor the Agent's Task Queue
python scripts/a2a_client.py --url http://searxng-agent.arpa/a2a/ --action list-tasks

# Note: Use --insecure to bypass SSL verification if needed.
```

---

### A2A JSON-RPC Endpoint Reference

All requests are sent as `POST` to the agent's A2A base URL with `Content-Type: application/json`. The `id`, `jsonrpc: "2.0"`, and `method` fields are always required in the request envelope.

#### Agent Discovery (HTTP GET — not JSON-RPC)

| Endpoint | Method | Description |
|---|---|---|
| `GET /.well-known/agent-card.json` | n/a | Retrieve the agent's capability card (name, skills, supported operations) |

---

#### Message Operations

| JSON-RPC Method | Request Type | Response Type | Description |
|---|---|---|---|
| `message/send` | `SendMessageRequest` | `SendMessageResponse` → `Task \| Message` | Send a message; returns a Task or immediate Message reply |
| `message/stream` | `StreamMessageRequest` | `StreamMessageResponse` (SSE) → `Task \| Message \| TaskStatusUpdateEvent \| TaskArtifactUpdateEvent` | Stream a message; server sends SSE events until completion |

**`message/send` payload shape:**
```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "<uuid>",
  "params": {
    "message": {
      "kind": "message",
      "role": "user",
      "parts": [{ "kind": "text", "text": "<your query>" }],
      "messageId": "<uuid>"
    },
    "configuration": { }
  }
}
```

**`message/stream` payload shape** — same as `message/send` but set `Accept: text/event-stream`. The server responds with SSE lines (`data: {...}`), ending with `[DONE]`.

---

#### Task Operations

| JSON-RPC Method | Request Type | Response/Error Type | Description |
|---|---|---|---|
| `tasks/get` | `GetTaskRequest` | `GetTaskResponse` → `Task` / `TaskNotFoundError` | Fetch the current state and history of a task by ID |
| `tasks/cancel` | `CancelTaskRequest` | `CancelTaskResponse` → `Task` / `TaskNotCancelableError \| TaskNotFoundError` | Cancel an in-progress task |
| `tasks/resubscribe` | `ResubscribeTaskRequest` | SSE stream of `TaskStatusUpdateEvent \| TaskArtifactUpdateEvent` | Re-attach an SSE stream to an already-running task (reconnect after drop) |

**`tasks/get` payload shape:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/get",
  "id": "<uuid>",
  "params": { "id": "<task_id>" }
}
```

**`tasks/cancel` payload shape:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/cancel",
  "id": "<uuid>",
  "params": { "id": "<task_id>" }
}
```

**`tasks/resubscribe` payload shape** — sends `TaskIdParams` (`{ "id": "<task_id>" }`), set `Accept: text/event-stream`.

---

#### Push Notification Operations

> [!NOTE]
> Push notification endpoints are optional. Agents that do not support them will return `PushNotificationNotSupportedError` (`-32003`).

| JSON-RPC Method | Request Type | Response/Error Type | Description |
|---|---|---|---|
| `tasks/pushNotification/set` | `SetTaskPushNotificationRequest` | `SetTaskPushNotificationResponse` → `TaskPushNotificationConfig` / `PushNotificationNotSupportedError` | Register a webhook/push URL to receive task status updates |
| `tasks/pushNotification/get` | `GetTaskPushNotificationRequest` | `GetTaskPushNotificationResponse` → `TaskPushNotificationConfig` / `PushNotificationNotSupportedError` | Retrieve the current push notification config for a task |
| `tasks/pushNotificationConfig/list` | `ListTaskPushNotificationConfigRequest` | `TaskPushNotificationConfig[]` / `PushNotificationNotSupportedError` | List all push notification configs (supports pagination via `ListTaskPushNotificationConfigParams`) |
| `tasks/pushNotificationConfig/delete` | `DeleteTaskPushNotificationConfigRequest` | `{}` / `PushNotificationNotSupportedError` | Delete a push notification config by its ID |

**`tasks/pushNotification/set` payload shape:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/pushNotification/set",
  "id": "<uuid>",
  "params": {
    "taskId": "<task_id>",
    "pushNotificationConfig": {
      "url": "https://my-receiver.example.com/webhook",
      "token": "<optional_auth_token>"
    }
  }
}
```

---

#### JSON-RPC Error Code Reference

| Code | Type | Meaning |
|---|---|---|
| `-32700` | `JSONParseError` | Invalid JSON payload |
| `-32600` | `InvalidRequestError` | Request payload validation error |
| `-32601` | `MethodNotFoundError` | Method not found / not implemented by this agent |
| `-32602` | `InvalidParamsError` | Invalid parameters |
| `-32603` | `InternalError` | Internal server error |
| `-32001` | `TaskNotFoundError` | The requested task ID does not exist |
| `-32002` | `TaskNotCancelableError` | Task exists but is in a terminal state and cannot be cancelled |
| `-32003` | `PushNotificationNotSupportedError` | This agent does not support push notifications |
| `-32004` | `UnsupportedOperationError` | This operation is not supported by this agent |
| `-32005` | `ContentTypeNotSupportedError` | Incompatible content types between client and server |
| `-32006` | `InvalidAgentResponseError` | The agent produced a response that violates the A2A schema |

---

#### Response Envelope

All non-streaming responses follow this JSON-RPC 2.0 envelope:
```json
{
  "jsonrpc": "2.0",
  "id": "<echoed_request_id>",
  "result": { ... },
  "error": { "code": -32001, "message": "Task not found", "data": null }
}
```
Only one of `result` or `error` will be present. Always check for `"error"` before reading `"result"`.

## Workflows

### 3. A2A & Subagent Methodologies (`docs/`)
Follow the patterns outlined in the `docs/` folder when designing workflows that involve spawning independent agent worker nodes:
- **A2A Orchestration**: Use explicit protocol interfaces when communicating between isolated AI agents. Ensure one agent serves as the coordinator while others act as execution workers.
- **Dispatching Parallel Agents**: Don't force one agent to do multiple isolated tasks sequentially. Spin up multiple isolated environments (or TMUX sessions) and invoke worker routines in parallel for faster results.
- **Subagent-Driven Development**: During complex execution tasks, break down the work into discrete chunks and farm it out to specialized subagents. You are the supervisor; they are the workers. Ensure they have clear constraints and output expected artifacts that you can subsequently review.

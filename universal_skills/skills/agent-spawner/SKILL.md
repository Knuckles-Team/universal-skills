---
name: agent-spawner
domain: agent-tools
skill_type: skill
description: >-
  Run one isolated delegated agent through the arbora `agents.run` operation.
  Use when a bounded task needs a temporary specialist without mutating the
  parent agent. Arbora admits the run, applies policy and records provenance.
tags: [agent, delegation, arbora, pydantic-ai, orchestration]
license: MIT
metadata:
  version: '1.5.2'
  author: Repository Maintainers
---

# Agent Spawner

Delegate one bounded task through the served arbora operation `agents.run`. The
caller sends one A2A message and an idempotency key. Arbora owns admission, the
model and tool grant, the run budget and the task record.

```text
act(op="agents.run", params={"message": {"role": "user", "parts": [{"text": "Inspect the configured tool catalog"}]}})
```

Poll the result with `ask(op="agents.tasks.get", params={"task_id": "<id>"})`.
Cancel with `act(op="agents.tasks.cancel", params={"task_id": "<id>"})`. Use
`find(intent="run an agent")` to see the current parameter schema.

Never put credentials in the message. Model, tool grant and TLS policy come from
the arbora deployment, not from this skill. The earlier in-process spawner and its
`AgentConfig` flags are retired.

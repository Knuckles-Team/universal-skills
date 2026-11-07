---
name: arbora-door
description: >-
  Use the arbora door: the six intent tools find, ask, why, write, act and
  manage that reach every operation, connector tool, skill and agent of the
  ecosystem from this coding harness. Use when a task needs platform knowledge,
  a connector, a registered agent or the shared workstream; before concluding
  that a capability is missing; or when a write needs a preview.
license: MIT
metadata:
  domain: core
  skill_type: skill
  tags: [arbora, door, mcp, intent-tools, workstream]
  version: '1.6.0'
---
# The arbora door

The arbora MCP server is the one door to the ecosystem. It exposes six intent
tools. Each takes `op="<operation id>"` with `params={...}`, or a
natural-language `intent="..."` with `op` empty.

| Tool | Use it to |
|---|---|
| `find` | Discover operations, connector tools, skills and agents, with their params |
| `ask` | Read: graph questions, records, workstreams, run status |
| `why` | Explain a result, a decision or a lineage |
| `write` | Record facts, checkpoints and other caller-owned writes |
| `act` | Run things: fleet tool calls, registered agents, workflows |
| `manage` | Configure the platform |

## Rules, in order

1. **Discover before concluding.** Call `find(intent="...")` before you decide
   that a capability is absent. `find(op="<id>")` returns one operation's spec
   and params schema.
2. **Preview a write, then resubmit.** `write`, `act` and `manage` answer a
   first call with a preview and a `plan_ref`. Read it, then resubmit the same
   call with that `plan_ref` and `execute=true`. Operations that declare no
   confirmation, such as the workstream operations, run on the first call.
3. **Reach a fleet tool through `act` with `fleet.call`.** Pass
   `params={"server": ..., "tool": ..., "arguments": {...}}`. `find` returns
   the server and tool names.
4. **Run a registered agent through `act` with `agents.run`.** Pass the agent
   profile and the task as `input`; report the run result as it is.

## The shared workstream

Every coding harness that carries this plugin joins one workstream per
workspace. The plugin attaches the session on the first prompt and records a
checkpoint before compaction. To hand off on purpose, follow the
`session-handoff` skill: `write` with `op="workstream.checkpoint"`. To pick up
what an earlier session left, `ask` with `op="workstream.get"` and the current
working directory as `workspace_root`.

## The status line

A plugin cannot set the main status line of every harness. To show the
workstream and the sign-in state, select the command
`arbora plugin statusline --harness <profile>` as the harness status line
command in its settings.

## Sign-in

The harness signs in to the door itself through the native client, with an
authorization code flow in the browser. A harness whose hooks run commands also
needs `arbora plugin login --harness <profile>` once; until then each hook
prints a one-line `AUTH_REQUIRED` note and never blocks the session.

---
name: canopy
description: >-
  Canopy is arbora's front door: the live architecture website and the entry point to the ecosystem through arbora's MCP door. Use it to reach every operation, connector tool, skill and agent from this coding harness with the six intent tools find, ask, why, write, act and manage.
license: MIT
metadata:
  domain: core
  skill_type: skill
  tags: [arbora, door, mcp, intent-tools, workstream]
  version: '1.6.2'
---
# Canopy

Scope: Canopy is arbora's front door: the live architecture website and the entry point to the ecosystem through arbora's MCP door. Use it to reach every operation, connector tool, skill and agent from this coding harness with the six intent tools find, ask, why, write, act and manage. Use when a task needs platform knowledge, a connector, a registered agent or the shared workstream; before concluding that a capability is missing; or when a write needs a preview.

Canopy is arbora's front door: the live architecture website, which grows
into a richer front door over time. This skill is the entry point that tells a
harness how to use the ecosystem through arbora and canopy. The arbora MCP
server is the one door to the ecosystem. It exposes six intent
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

## Steps

1. Discover the capability with `find(intent="<what you need>")`. Verify that the result lists at least one matching operation with its params schema.
2. Read the single operation with `find(op="<operation id>")`. Verify that the params you plan to send match the returned schema.
3. Send the call through the right tool, for example `act(op="fleet.call", params={"server": ..., "tool": ..., "arguments": {...}})`. Verify that a write, act or manage call returns a preview with a `plan_ref`.
4. Resubmit the same call with `execute=true` and the returned `plan_ref`. Verify that the response reports the run result rather than another preview.
5. To hand off, record a checkpoint with `write(op="workstream.checkpoint", ...)`. Verify that `ask(op="workstream.get", params={"workspace_root": "<cwd>"})` returns the checkpoint.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Hook prints `AUTH_REQUIRED` | Harness not signed in to the door | Run `arbora plugin login --harness <profile>` once and complete the browser flow. |
| Capability seems absent | `find` was not called or the intent was too narrow | Re-run `find(intent="...")` with different wording before concluding it is missing. |
| Write returns only a preview | `plan_ref` and `execute=true` not sent | Resubmit the identical call with the returned `plan_ref` and `execute=true`. |
| Status line shows no workstream | Status line command not selected in harness settings | Set `arbora plugin statusline --harness <profile>` as the harness status line command. |

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

---
name: unattended-loop-driver
domain: agent-tools
skill_type: skill
description: >-
  Run Claude Code unattended ("while you sleep") to drive the arbora Loop engine — feature extraction + innovation distillation — behind a governance-derived permission fence. Use when the user wants to "run the loop overnight", "let Claude work unattended", "run while I sleep", "set up an autonomous build session", or "drive the evolution loop without babysitting".
license: MIT
tags: [claude-code, unattended, permission-fence, knowledge-graph, golden-loop, self-evolution, safety, orchestration]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
  concepts: [OS-5.40, OS-5.41, ECO-4.47, SAFE-1.8]
---

# Unattended Loop Driver

Scope: Run Claude Code unattended ("while you sleep") to drive the arbora Loop engine — feature extraction + innovation distillation — behind a governance-derived permission fence. Use when the user wants to "run the loop overnight", "let Claude work unattended", "run while I sleep", "set up an autonomous build session", or "drive the evolution loop without babysitting". Verifies the fence is active (settings.json allow/ask/deny + .claudeignore, no bypassPermissions), then loops graph_loops(action="run") committing per productive cycle, halts on any ask/deny verdict instead of auto-approving, and writes a morning summary to MEMORY.md for review.

Let Claude Code run **unattended** and drive the existing arbora **Loop engine**
(`LoopController`, KG-2.78) — the same feature-extraction + innovation-distillation
cycle the daemon ticks — inside a **permission fence** so the worst it can do is
harmless. This surpasses a hand-written `settings.json`: the fence is **derived
from the live `ActionPolicy`** and **self-updating** (OS-5.40), and a **dynamic
PreToolUse gate** (OS-5.41) consults governance at decision time.

## 1. Draw the fence (once)

Generate the governance-derived Claude Code permission fence + `.claudeignore`:

```bash
meristem harness-fence --target ~/.claude            # or <project>/.claude
# or via MCP:  graph_configure(action="harness_fence", config_key="~/.claude")
```

This writes `settings.json` with `defaultMode=acceptEdits`, an `allow` list of
routine reversible work, an `ask` list of medium-stakes actions, and a `deny`
wall (rm -rf, force-push, hard reset, secret files, raw curl) regenerated from
`ActionPolicy` each run — **never** `bypassPermissions`. The companion
`.claudeignore` keeps secrets out of context entirely.

**Verify before walking away** (`--dry-run` prints without writing):

```bash
meristem harness-fence --target ~/.claude --dry-run
```

Confirm `defaultMode == "acceptEdits"`, `bypassPermissions` absent, and the deny
list contains the irreversible + secret rules.

## Steps

1. Preview the fence with `meristem harness-fence --target ~/.claude --dry-run`. Verify that the output shows `defaultMode` as `acceptEdits`, no `bypassPermissions`, and a deny list that includes force-push, hard reset and secret files.
2. Write the fence with `meristem harness-fence --target ~/.claude`. Verify with `grep -c bypassPermissions ~/.claude/settings.json` that the count is 0 and that `.claudeignore` exists next to it.
3. Start the run with `meristem sleep-run --max-cycles 6 --max-topics 5 --workspace .`, or hand Claude the goal prompt from section 2. Verify that it prints a JSON report containing `cycles_run` and `stop_reason`.
4. Review the morning summary with `git log --oneline -n 10` and `grep -n "" MEMORY.md | tail -40`. Verify that `commits` in the report matches the new commits and that `summary_path` points to the written `MEMORY.md`.
5. Approve or reject the `ask`-list actions that the gate halted. Verify that each halted action is recorded in the summary before you approve it.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `settings.json` lacks the deny rules | Fence was generated without the governance policy or arbora was down | Rerun `meristem harness-fence --target ~/.claude` once arbora responds, and recheck with `--dry-run` before leaving |
| Run stops with `max_cycles` and unfinished work | Cap reached before convergence | Review the summary and start another run with a larger `--max-cycles` |
| An action was halted by the gate | It sits on the `ask` list, so unattended runs cannot approve it | Review it in the morning and run the action yourself, or move it to `allow` through governance policy |
| Same failure repeated three times | The agent could not fix a blocker | Read the note it wrote to `MEMORY.md`, fix the blocker manually, and rerun |

## 2. Hand off the run

Give Claude a clear goal and let it loop the engine. The handoff prompt:

```text
Goal for this run: [describe the full outcome].

Work toward it autonomously under the permission fence in settings.json:
- Read what you need, edit source, run tests and lint as you go.
- Drive the arbora Loop once per iteration: graph_loops(action="run", max_topics=5)
  (feature extraction + innovation distillation, propose-only).
- Commit after each productive cycle with a clear message.
- If a tool hits the ask list (the gate returns "ask"), STOP that action and
  leave a note — never try to force it through (SAFE-1.8).
- If you fail the same thing 3 times, stop and write what you tried.

When done or stuck, write a summary to MEMORY.md: what changed, what's left,
and anything I need to review.
```

## 3. Or run the loop driver directly

The whole loop is a single command — the testable core behind this skill:

```bash
meristem sleep-run --max-cycles 6 --max-topics 5 --workspace .
```

It drives `LoopController.run_one_cycle` until the loop **converges** (no new
progress for 2 cycles) or the cap is hit, commits per productive cycle, and
writes the morning summary into `MEMORY.md`.

## 4. Morning review

The summary is written into `MEMORY.md` between stable markers, so the existing
memory bridge (`inject_project_context`, KG-2.1) surfaces it on the next
SessionStart. Read the commit history, the summary, and the diff; approve the one
or two `ask`-list items the gate halted.

## Guarantees

- **deny > allow > ask** — safety rules can never be overridden by a broad allow.
- **Fail-closed gate** — the PreToolUse gate denies on any error/unparsable input
  and protects secrets even when the arbora daemon is down.
- **Propose-only loop** — `graph_loops(action="run")` writes proposals (specs,
  skill candidates, team proposals); it never auto-merges or executes high-stakes
  actions.
- **ask = halt, never auto-approve** — an unattended session has no human to
  answer, so an `ask` verdict stops the action and queues it for the morning
  (SAFE-1.8 containment).

## Output

A JSON session report: `cycles_run`, `productive_cycles`, `commits`,
`stop_reason` (`converged` | `max_cycles`), `elapsed_s`, and `summary_path`
(the `MEMORY.md` written for review).

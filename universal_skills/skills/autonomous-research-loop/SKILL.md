---
name: autonomous-research-loop
domain: agent-tools
skill_type: skill
description: >-
  Runs one propose-only self-evolution "golden loop" cycle over the Knowledge Graph. Use when the user wants to "run the research loop", "evolve the knowledge graph", "find and address open topics", "propose specs/teams from the KG", or "self-improve the codebase". Never auto-merges or executes anything — every artifact is a draft/proposal a human reviews.
license: MIT
tags: [knowledge-graph, research, self-evolution, golden-loop, propose-only, orchestration]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

# Autonomous Research Loop (propose-only)

Scope: Runs one propose-only self-evolution "golden loop" cycle over the Knowledge Graph. Use when the user wants to "run the research loop", "evolve the knowledge graph", "find and address open topics", "propose specs/teams from the KG", or "self-improve the codebase". Intake of unresolved topics → acquire related sources → ADDRESSES-resolve (converge) → optional distil spec DRAFTS into .specify/ → synthesize a team PROPOSAL. Never auto-merges or executes anything — every artifact is a draft/proposal a human reviews.

Drives the KG's self-evolution **golden loop** — one cycle of:

1. **Intake** — unresolved `Concept` topics (no `ADDRESSED_BY` edge).
2. **Acquire** — semantically related sources per topic (vector search over the
   KG; optional external X/SearXNG/scholarx when `KG_RESEARCH_EXTERNAL=1`).
3. **Resolve** — write `ADDRESSES` / `ADDRESSED_BY` edges so the loop **converges**
   (addressed topics stop re-surfacing; new open topics rise).
4. **Distil** *(optional, `KG_GOLDEN_DISTILL=1`)* — `SpecDraft` markdown written
   to `.specify/specs/kg-distilled/` (DRAFTS only).
5. **Synthesize** — a `TeamSpec`/`AgentSpec` **proposal** addressing the topics,
   persisted to the KG (not executed).

**Propose-only guarantee:** no code execution, no PR merge, no edits outside
`.specify/` drafts and KG proposal nodes.

## Run it

On-demand via the arbora MCP orchestration tool:

```text
graph_orchestrate(action="golden_loop", max_topics=5)
```

…or directly:

```bash
KG_DAEMON_ROLE=client python -c \
  "from meristem.knowledge_graph.research.golden_loop import run_golden_loop_cycle; \
   import json; print(json.dumps(run_golden_loop_cycle(max_topics=5), default=str, indent=2))"
```

## Steps

1. Check the prerequisites by confirming the graph backend responds, for example with `graph_query` on a trivial label count. Verify that it returns without a connection error and that embeddings exist.
2. Run one cycle with `graph_orchestrate(action="golden_loop", max_topics=5)`. Verify that the call returns the JSON report with `topics_intake` and `topics_resolved` fields.
3. Inspect the report for `errors` and `spec_drafts`. Verify that `errors` is empty and any `spec_drafts` paths exist under `.specify/specs/kg-distilled/` with `ls`.
4. Confirm the loop converged by re-running with `max_topics=5`. Verify that resolved topics no longer appear in `topics_intake`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `topics_intake` is always 0 | No unresolved `Concept` topics | Ingest new concepts into the KG, then re-run the cycle. |
| Acquire finds no sources | Embeddings not backfilled | Wait for the host daemon `embed_backfill` thread to finish, then re-run. |
| Direct python run cannot reach the graph | `KG_DAEMON_ROLE=client` not set or backend unreachable | Export `KG_DAEMON_ROLE=client`, confirm the backend is up, and re-run the `run_golden_loop_cycle` command. |
| No spec drafts written | Distil disabled | Set `KG_GOLDEN_DISTILL=1` and re-run. |

## Always-on daemon (optional)

Set `KG_GOLDEN_LOOP=1` (interval `KG_GOLDEN_LOOP_INTERVAL`, default 3600s) on the
**host daemon** (gateway / `arbora-daemon`) to run the cycle continuously and
throttled behind the foreground gate. Off by default (autonomous LLM work is
opt-in). Still propose-only.

## Output

A JSON report: `topics_intake`, `topics_resolved`, `sources_linked`,
`spec_drafts` (paths), `team` (lead + members + persisted node/edge counts),
`errors`.

## Prerequisites

- Embeddings backfilled (the host daemon's `embed_backfill` thread) so acquire's
  vector search has substrate.
- A reachable graph backend (tiered: epistemic L1 + pggraph L3).

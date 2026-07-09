---
name: autonomous-research-loop
domain: agent-tools
skill_type: skill
description: >-
  Runs one propose-only self-evolution "golden loop" cycle over the Knowledge Graph.
  Use when the user wants to "run the research loop", "evolve the knowledge graph",
  "find and address open topics", "propose specs/teams from the KG", or "self-improve the codebase".
  Intake of unresolved topics → acquire related sources → ADDRESSES-resolve (converge) →
  optional distil spec DRAFTS into .specify/ → synthesize a team PROPOSAL. Never auto-merges
  or executes anything — every artifact is a draft/proposal a human reviews.
license: MIT
tags: [knowledge-graph, research, self-evolution, golden-loop, propose-only, orchestration]
metadata:
  version: '1.1.0'
  author: Genius
---

# Autonomous Research Loop (propose-only)

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

On-demand via the graph-os MCP orchestration tool:

```text
graph_orchestrate(action="golden_loop", max_topics=5)
```

…or directly:

```bash
KG_DAEMON_ROLE=client python -c \
  "from agent_utilities.knowledge_graph.research.golden_loop import run_golden_loop_cycle; \
   import json; print(json.dumps(run_golden_loop_cycle(max_topics=5), default=str, indent=2))"
```

## Always-on daemon (optional)

Set `KG_GOLDEN_LOOP=1` (interval `KG_GOLDEN_LOOP_INTERVAL`, default 3600s) on the
**host daemon** (gateway / `graph-os-daemon`) to run the cycle continuously and
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

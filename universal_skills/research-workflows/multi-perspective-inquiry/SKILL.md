---
name: multi-perspective-inquiry
skill_type: workflow
description: >-
  On-demand multi-perspective (STORM) research inquiry — derive expert lenses, fan KG
  probes across their questions, map agreements/contradictions/blind-spots, and self-critique.
  Delegates to the native engine (research_artifact action=inquire) so the prompts never drift.
domain: research-workflows
agent: research_coordinator
team_config:
  name: perspectival_inquiry_team
  task_pattern: multi-perspective research inquiry and synthesis
  execution_mode: sequential
  specialist_ids:
    - inquiry-agent
  tool_assignments:
    inquiry-agent: [research_artifact, graph_query]
tags: [research, storm, multi-perspective, contradiction-map]
metadata:
  version: '1.2.1'
---

# Multi-Perspective Inquiry Workflow (STORM, native)

Implements the native perspectival-inquiry engine (agent-utilities concepts KG-2.127 /
KG-2.128 / KG-2.129).

Run Stanford's STORM method as a single delegated call to the native perspectival-inquiry
engine in `agent-utilities` — distinct expert lenses ask different questions, the KG answers
each, and the result is a contradiction/agreement/blind-spot map plus a peer-review
self-critique whose frontier question is submitted as the next research loop.

This workflow is the **on-demand twin** of the loop's default behaviour: it does not
re-implement the STORM prompts, it calls `research_artifact action=inquire` (which the loop
also uses), so the two surfaces never drift.

## Steps

### Step 1: Inquire
**Agent**: `inquiry-agent`
**Tools**: `research_artifact`

Call `research_artifact` with `action=inquire` and `topic=<the topic>`. The engine derives
the expert lenses, fans `acquire_for_topic` across each lens's questions, builds the
contradiction/agreement/blind-spot map, runs the peer-review, and (by default) materializes
the inquiry as typed KG nodes. Expected: `inquiry_briefing` — perspectives + agreements +
divergences + blind_spot + peer_review (dominant/missing lens, confidence, frontier question).

### Step 2: Read Back [depends_on: inquire]
**Agent**: `inquiry-agent`
**Tools**: `graph_query`

Query the materialized inquiry subgraph (`research_inquiry` / `perspective` / `agreement` /
`contradiction` / `blind_spot` / `peer_review` nodes) to present the briefing and surface
the frontier question that was queued as the next research loop. Expected:
`perspectival_briefing`.

## Execution

This is a thin delegating workflow. Execute it via graph-os rather than re-prompting:

- MCP: `research_artifact(action="inquire", topic="<topic>")`
- REST: `POST /api/research/inquire {"topic": "<topic>"}`
- Or run the whole workflow through `graph_orchestrate(action="execute_workflow",
  agent_name="multi-perspective-inquiry", task="<topic>")`.

The native engine is the single source of truth (`knowledge_graph/research/perspective.py`);
this skill only orchestrates the call and reads back the result.

---
name: meme-factory-pipeline
skill_type: workflow
description: >-
  Draft caption copy and render it composed onto a visual asset, then run a final
  readiness check. Use when a user has supplied a topic/reference and voice
  constraints and wants a review-ready meme image; this workflow never posts or
  schedules it.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: meme-factory-pipeline-team
  task_pattern: meme caption drafting and visual composition
  execution_mode: sequential
  specialist_ids:
    - content-draft-writer
    - canvas-design
    - publication-preflight
tags: [social, content, meme, design]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.1'
  author: Genius
---

# Meme Factory Pipeline Workflow

Compose the named atomic skills without adding posting or scheduling logic
here.

## Inputs

Provide the topic/reference, voice guide, and publication requirements.

## Steps

### Step 0: content-draft-writer [skill: content-draft-writer]

Invoke `$content-draft-writer` with the workflow inputs to draft the
caption copy.

Expected: `caption_draft`

### Step 1: canvas-design [skill: canvas-design] [depends_on: Step 0]

Invoke `$canvas-design` with `caption_draft` to render the composed
meme image.

Expected: `meme_image`

### Step 2: publication-preflight [skill: publication-preflight] [depends_on: Step 1]

Invoke `$publication-preflight` with `meme_image` and the publication
requirements.

Expected: `readiness_decision`

## Output

Return `meme_image` and `readiness_decision`. Do not post or schedule it.

## Execution

- **Run first:** Step 0 — `$content-draft-writer`.
- **After level 0:** Step 1 — `$canvas-design`.
- **After level 1:** Step 2 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

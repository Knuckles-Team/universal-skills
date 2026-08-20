---
name: presentation-builder
skill_type: workflow
description: >-
  Outline and draft the talk track, render it as Marp presentation slides, and
  run a final readiness check. Use when a user has supplied a topic, audience,
  and voice constraints and wants review-ready slides; this workflow never
  publishes or presents it.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: presentation-builder-team
  task_pattern: sourced slide-deck drafting and readiness review
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - marp-presentations
    - publication-preflight
tags: [social, content, presentation, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Presentation Builder Workflow

Compose the named atomic skills without adding new slide-rendering logic here.

## Inputs

Provide the topic, audience, objective, length constraints, and voice guide.

## Steps

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs and
`approved_outline` to draft the talk track.

Expected: `talk_track_draft`

### Step 2: marp-presentations [skill: marp-presentations] [depends_on: Step 1]

Invoke `$marp-presentations` with `talk_track_draft` and
`approved_outline` to render the Marp slide deck.

Expected: `slide_deck`

### Step 3: publication-preflight [skill: publication-preflight] [depends_on: Step 2]

Invoke `$publication-preflight` with `slide_deck` and the publication
requirements.

Expected: `readiness_decision`

## Output

Return `slide_deck` and `readiness_decision`. Do not publish or present it.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$marp-presentations`.
- **After level 2:** Step 3 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

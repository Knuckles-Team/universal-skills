---
name: video-content-pipeline
skill_type: workflow
description: >-
  Outline and draft a video script, produce the edited video asset, and run a
  final readiness check. Use when a user has supplied a topic, audience, and
  voice constraints and wants a review-ready video; this workflow never
  publishes or uploads it.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: video-content-pipeline-team
  task_pattern: sourced video script drafting and asset production
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - creative-media
    - publication-preflight
tags: [social, content, video, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Video Content Pipeline Workflow

Compose the named atomic skills without adding publishing logic here.

## Inputs

Provide the topic, audience, length constraints, and voice guide.

## Steps

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs and
`approved_outline` to draft the video script.

Expected: `video_script`

### Step 2: creative-media [skill: creative-media] [depends_on: Step 1]

Invoke `$creative-media` with `video_script` to produce the edited
video asset.

Expected: `video_asset`

### Step 3: publication-preflight [skill: publication-preflight] [depends_on: Step 2]

Invoke `$publication-preflight` with `video_asset` and the
publication requirements.

Expected: `readiness_decision`

## Output

Return `video_asset` and `readiness_decision`. Do not publish or upload it.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$creative-media`.
- **After level 2:** Step 3 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: social-media-campaign
skill_type: workflow
description: >-
  Outline, draft, and edit sourced social post copy, render matching visual
  assets, and run a final readiness check. Use when a user has supplied a
  campaign objective, audience, and voice constraints and wants review-ready
  posts; this workflow never posts or schedules the campaign.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: social-media-campaign-team
  task_pattern: sourced social post copy and visual-asset drafting
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - copy-editor
    - canvas-design
    - publication-preflight
tags: [social, content, campaign, design]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Social Media Campaign Workflow

Compose the named atomic skills without adding posting or scheduling logic
here.

## Inputs

Provide the campaign objective, audience, channel constraints, and voice guide.

## Steps

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs and
`approved_outline`.

Expected: `post_drafts`

### Step 2: copy-editor [skill: copy-editor] [depends_on: Step 1]

Invoke `$copy-editor` with `post_drafts` and the workflow inputs.

Expected: `edited_posts`

### Step 3: canvas-design [skill: canvas-design] [depends_on: Step 2]

Invoke `$canvas-design` with `edited_posts` to render matching
visual assets.

Expected: `campaign_visual_assets`

### Step 4: publication-preflight [skill: publication-preflight] [depends_on: Step 3]

Invoke `$publication-preflight` with `edited_posts`,
`campaign_visual_assets`, and the publication requirements.

Expected: `readiness_decision`

## Output

Return `edited_posts`, `campaign_visual_assets`, and `readiness_decision`. Do
not post or schedule the campaign.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$copy-editor`.
- **After level 2:** Step 3 — `$canvas-design`.
- **After level 3:** Step 4 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

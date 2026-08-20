---
name: email-campaign-builder
skill_type: workflow
description: >-
  Outline, draft, and edit sourced email campaign copy, then run a final
  readiness check. Use when a user has supplied a campaign objective, audience,
  and voice constraints and wants review-ready campaign copy; this workflow
  never sends or schedules the campaign.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: email-campaign-builder-team
  task_pattern: sourced email campaign copy drafting and readiness review
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - copy-editor
    - publication-preflight
tags: [social, content, email, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Email Campaign Builder Workflow

Compose the named atomic skills without adding sending or scheduling logic
here.

## Inputs

Provide the campaign objective, audience segment, voice guide, and publication
requirements.

## Steps

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs and
`approved_outline`.

Expected: `campaign_draft`

### Step 2: copy-editor [skill: copy-editor] [depends_on: Step 1]

Invoke `$copy-editor` with `campaign_draft` and the workflow inputs.

Expected: `edited_campaign`

### Step 3: publication-preflight [skill: publication-preflight] [depends_on: Step 2]

Invoke `$publication-preflight` with `edited_campaign` and the
publication requirements.

Expected: `readiness_decision`

## Output

Return `edited_campaign` and `readiness_decision`. Do not send or schedule the
campaign.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$copy-editor`.
- **After level 2:** Step 3 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

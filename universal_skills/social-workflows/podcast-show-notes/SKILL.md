---
name: podcast-show-notes
skill_type: workflow
description: >-
  Outline, draft, and edit show notes from a supplied episode transcript, then
  run a final readiness check. Use when a user has an approved transcript,
  audience, and voice constraints and wants review-ready show notes; this
  workflow never publishes or uploads them.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: podcast-show-notes-team
  task_pattern: transcript-sourced show-notes drafting and readiness review
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - copy-editor
    - publication-preflight
tags: [social, content, podcast, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.3.0'
  author: Genius
---

# Podcast Show Notes Workflow

Compose the named atomic skills without adding transcription logic here.

## Inputs

Provide the episode transcript, audience, voice guide, and publication
requirements.

## Steps

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs and the
episode transcript.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs, the episode
transcript, and `approved_outline`.

Expected: `show_notes_draft`

### Step 2: copy-editor [skill: copy-editor] [depends_on: Step 1]

Invoke `$copy-editor` with `show_notes_draft` and the workflow
inputs.

Expected: `edited_show_notes`

### Step 3: publication-preflight [skill: publication-preflight] [depends_on: Step 2]

Invoke `$publication-preflight` with `edited_show_notes` and the
publication requirements.

Expected: `readiness_decision`

## Output

Return `edited_show_notes` and `readiness_decision`. Do not publish or upload
them.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$copy-editor`.
- **After level 2:** Step 3 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

---
name: blog-post-generator
domain: social-workflows
skill_type: workflow
description: >-
  Research, outline, draft, verify, edit, and preflight a sourced blog post by
  composing the catalog's atomic research and content skills. Use when a user has
  supplied a topic, audience, objective, channel constraints, and publication
  requirements and wants a review-ready post; this workflow never publishes it.
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: blog-post-generator-team
  task_pattern: sourced blog post drafting and readiness review
  execution_mode: sequential
  specialist_ids:
    - web-search
    - content-outline-builder
    - content-draft-writer
    - citation-auditor
    - copy-editor
    - publication-preflight
tags: [social, content, blog, research, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.2.1'
  author: Genius
---

# Blog Post Generator Workflow

Compose the named atomic skills without adding editorial or publication logic here.

## Inputs

Provide the topic, audience, objective, channel and length constraints, voice guide,
citation style, publication requirements, and any approved sources or exclusions.

## Steps

### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs.

Expected: `source_packet`

### Step 1: content-outline-builder [skill: content-outline-builder] [depends_on: Step 0]

Invoke `$content-outline-builder` with the workflow inputs and `source_packet`.

Expected: `approved_outline`

### Step 2: content-draft-writer [skill: content-draft-writer] [depends_on: Step 1]

Invoke `$content-draft-writer` with the workflow inputs, `source_packet`, and
`approved_outline`.

Expected: `sourced_draft`

### Step 3: citation-auditor [skill: citation-auditor] [depends_on: Step 2]

Invoke `$citation-auditor` with `sourced_draft` and `source_packet`.

Expected: `citation_audit`

### Step 4: copy-editor [skill: copy-editor] [depends_on: Step 3]

Invoke `$copy-editor` with `sourced_draft`, `citation_audit`, and the workflow inputs.

Expected: `edited_draft`

### Step 5: publication-preflight [skill: publication-preflight] [depends_on: Step 4]

Invoke `$publication-preflight` with `edited_draft`, `citation_audit`, and the
publication requirements.

Expected: `readiness_decision`

## Output

Return `edited_draft`, `citation_audit`, and `readiness_decision`. Do not publish,
schedule, send, or upload the post.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After Step 0:** Step 1 — `$content-outline-builder`.
- **After Step 1:** Step 2 — `$content-draft-writer`.
- **After Step 2:** Step 3 — `$citation-auditor`.
- **After Step 3:** Step 4 — `$copy-editor`.
- **After Step 4:** Step 5 — `$publication-preflight`.

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

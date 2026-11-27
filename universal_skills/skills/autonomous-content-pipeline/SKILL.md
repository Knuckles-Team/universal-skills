---
name: autonomous-content-pipeline
skill_type: workflow
description: >-
  Research, outline, draft, verify, edit, and preflight a batch of sourced
  content pieces by composing the catalog's atomic research and content skills,
  unattended. Use when a user has supplied a topic list, audience, objective, and
  publication requirements and wants review-ready drafts produced without manual
  handoffs between steps; this workflow never publishes.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: autonomous-content-pipeline-team
  task_pattern: unattended batch content drafting and readiness review
  execution_mode: sequential
  specialist_ids:
    - web-search
    - content-outline-builder
    - content-draft-writer
    - citation-auditor
    - copy-editor
    - publication-preflight
tags: [social, content, automation, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Autonomous Content Pipeline Workflow

Compose the named atomic skills without adding editorial or publication logic
here.

## Inputs

Provide the topic list, audience, objective, channel and length constraints,
voice guide, citation style, and publication requirements.

## Steps

1. Gather sources for each topic by invoking `$web-search` with the workflow inputs. Verify that `source_packet` has at least one source per topic.
2. Build outlines by invoking `$content-outline-builder` with `source_packet`. Verify that `approved_outline` matches the audience and length constraints.
3. Write drafts by invoking `$content-draft-writer` with the outline and sources. Verify that `sourced_draft` cites sources from `source_packet`.
4. Audit citations by invoking `$citation-auditor` with `sourced_draft`. Verify that `citation_audit` flags any unsupported claim.
5. Edit each draft by invoking `$copy-editor` with the draft and audit. Verify that `edited_draft` follows the voice guide and resolves the flagged claims.
6. Check readiness by invoking `$publication-preflight` with `edited_draft`. Verify that `readiness_decision` is recorded for every topic and nothing was published.


### Step 0: web-search [skill: web-search]

Invoke `$web-search` with the workflow inputs for each topic.

Expected: `source_packet`

### Step 1: content-outline-builder [skill: content-outline-builder] [depends_on: Step 0]

Invoke `$content-outline-builder` with the workflow inputs and
`source_packet`.

Expected: `approved_outline`

### Step 2: content-draft-writer [skill: content-draft-writer] [depends_on: Step 1]

Invoke `$content-draft-writer` with the workflow inputs,
`source_packet`, and `approved_outline`.

Expected: `sourced_draft`

### Step 3: citation-auditor [skill: citation-auditor] [depends_on: Step 2]

Invoke `$citation-auditor` with `sourced_draft` and `source_packet`.

Expected: `citation_audit`

### Step 4: copy-editor [skill: copy-editor] [depends_on: Step 3]

Invoke `$copy-editor` with `sourced_draft`, `citation_audit`, and the
workflow inputs.

Expected: `edited_draft`

### Step 5: publication-preflight [skill: publication-preflight] [depends_on: Step 4]

Invoke `$publication-preflight` with `edited_draft`,
`citation_audit`, and the publication requirements.

Expected: `readiness_decision`

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| A topic has no sources | Query too narrow | Rewrite that topic's query more broadly and re-invoke `$web-search` for it only |
| Citation audit flags claims | Draft states facts absent from the sources | Send the flagged claims back to `$content-draft-writer` to cite or remove them |
| Preflight blocks a piece | Missing publication requirement such as a disclosure | Add the missing item to the draft and re-run `$publication-preflight` |
| Batch stalls on one topic | An upstream step failed for that topic | Mark that topic as failed in the output and continue the remaining topics |

## Output

Return `edited_draft`, `citation_audit`, and `readiness_decision` for each
topic. Do not publish, schedule, send, or upload any piece.

## Execution

- **Run first:** Step 0 — `$web-search`.
- **After level 0:** Step 1 — `$content-outline-builder`.
- **After level 1:** Step 2 — `$content-draft-writer`.
- **After level 2:** Step 3 — `$citation-auditor`.
- **After level 3:** Step 4 — `$copy-editor`.
- **After level 4:** Step 5 — `$publication-preflight`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

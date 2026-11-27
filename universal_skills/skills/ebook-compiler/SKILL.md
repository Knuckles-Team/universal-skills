---
name: ebook-compiler
skill_type: workflow
description: >-
  Outline, draft, and edit a multi-chapter manuscript, then merge the chapters
  into one compiled document and run a final readiness check. Use when a user has
  an approved chapter list, audience, and voice constraints and wants a
  review-ready compiled ebook; this workflow never publishes or uploads it.
domain: social-workflows
license: MIT
requires: []
agent: content-orchestrator
team_config:
  name: ebook-compiler-team
  task_pattern: multi-chapter manuscript drafting and compilation
  execution_mode: sequential
  specialist_ids:
    - content-outline-builder
    - content-draft-writer
    - copy-editor
    - document-tools
    - publication-preflight
tags: [social, content, ebook, editorial]
concept: CONCEPT:SOCIAL-001
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Ebook Compiler Workflow

Compose the named atomic skills without adding new binding/formatting logic
here.

## Inputs

Provide the chapter outline list, audience, voice guide, and publication
requirements.

## Steps

1. Build the outline with `$content-outline-builder` for each chapter. Verify that `approved_outline` lists every requested chapter.
2. Draft the chapters with `$content-draft-writer` using `approved_outline`. Verify that `chapter_drafts` has one draft per outline entry.
3. Edit the drafts with `$copy-editor`. Verify that `edited_chapters` keeps the same chapter count as `chapter_drafts`.
4. Merge the chapters with `$document-tools` into one document. Verify that `compiled_manuscript` contains all chapters in outline order.
5. Run `$publication-preflight` on `compiled_manuscript` with the publication requirements. Verify that `readiness_decision` is recorded and that nothing was published or uploaded.

### Step 0: content-outline-builder [skill: content-outline-builder]

Invoke `$content-outline-builder` with the workflow inputs for each
chapter.

Expected: `approved_outline`

### Step 1: content-draft-writer [skill: content-draft-writer] [depends_on: Step 0]

Invoke `$content-draft-writer` with the workflow inputs and
`approved_outline` to draft each chapter.

Expected: `chapter_drafts`

### Step 2: copy-editor [skill: copy-editor] [depends_on: Step 1]

Invoke `$copy-editor` with `chapter_drafts` and the workflow inputs.

Expected: `edited_chapters`

### Step 3: document-tools [skill: document-tools] [depends_on: Step 2]

Invoke `$document-tools` with `edited_chapters` to merge them into
one compiled manuscript document.

Expected: `compiled_manuscript`

### Step 4: publication-preflight [skill: publication-preflight] [depends_on: Step 3]

Invoke `$publication-preflight` with `compiled_manuscript` and the
publication requirements.

Expected: `readiness_decision`

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Outline missing chapters | Chapter list input was incomplete | Re-invoke `$content-outline-builder` with the full approved chapter list. |
| Merged manuscript is out of order | Chapters passed to `$document-tools` unsorted | Reorder `edited_chapters` to match `approved_outline` and re-run the merge. |
| `readiness_decision` is not ready | Preflight found unmet publication requirements | Read the findings, return to `$copy-editor` for the flagged chapters and rerun the merge and preflight. |

## Output

Return `compiled_manuscript` and `readiness_decision`. Do not publish, schedule,
send, or upload the ebook.

## Execution

- **Run first:** Step 0 — `$content-outline-builder`.
- **After level 0:** Step 1 — `$content-draft-writer`.
- **After level 1:** Step 2 — `$copy-editor`.
- **After level 2:** Step 3 — `$document-tools`.
- **After level 3:** Step 4 — `$publication-preflight`.

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.

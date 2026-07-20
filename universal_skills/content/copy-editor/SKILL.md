---
name: copy-editor
domain: content
skill_type: skill
description: >-
  Edit an existing draft for clarity, coherence, concision, grammar, terminology,
  and adherence to a supplied voice or style guide without changing its supported
  meaning. Use when a draft is factually settled and needs an editorial pass. Do not
  use to perform research, verify citations, add new factual claims, or publish the
  result.
license: MIT
tags: [content, editing, clarity, style, grammar]
metadata:
  version: '1.2.1'
  author: Genius
---

# Copy Editor

Improve the supplied draft while preserving its intent, evidence, citations, and
authorial constraints.

## Editing boundaries

- Correct grammar, spelling, punctuation, syntax, repetition, ambiguity, and weak transitions.
- Normalize terminology, capitalization, headings, lists, and style-guide conventions.
- Tighten prose without deleting necessary qualifications or uncertainty.
- Preserve citation anchors and quoted meaning. Never "improve" a quotation.
- Flag suspected factual, legal, medical, financial, or policy problems rather than
  resolving them through unsourced rewriting.
- Do not add claims, examples, statistics, endorsements, or links not present in the draft.

## Output

Return the edited draft and a short change note covering material structural edits,
unresolved ambiguities, style-guide conflicts, and items requiring author or subject-
matter approval. For high-sensitivity text, show proposed changes without overwriting
the source unless the user explicitly requests an in-place edit.

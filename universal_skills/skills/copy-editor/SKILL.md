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
  version: '1.6.2'
  author: Knuckles-Team
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

## Steps

1. Read the draft and the style guide before editing.
   Run `wc -w draft.md` and `ls`. Verify that you know the voice rules and the sensitivity level.
2. Apply edits within the boundaries to a working copy.
   Run `cp draft.md draft.edited.md` first. Verify that the original file is unchanged.
3. Normalize terminology and conventions.
   Use `grep -n -i "<variant spelling>" draft.edited.md` for each inconsistent term. Verify that every variant resolves to one form.
4. Confirm citations and quotations survived intact.
   Run `diff <(grep -o "\[[^]]*\]" draft.md) <(grep -o "\[[^]]*\]" draft.edited.md)`. Verify that the diff is empty.
5. Write the change note listing structural edits, ambiguities, conflicts, and approvals needed.
   Run `grep -n -i "flag" change-note.md`. Verify that every flagged factual concern is listed rather than rewritten.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Citation anchors changed after editing | Over-aggressive rewriting | Restore them from `draft.md` and redo the edit around the anchor |
| Draft states a doubtful fact | Possible factual or legal error | Flag it in the change note for the author and leave the sentence unchanged |
| Style guide conflicts with the author's voice | Competing rules | List the conflict in the change note and ask for a ruling before changing |

## Output

Return the edited draft and a short change note covering material structural edits,
unresolved ambiguities, style-guide conflicts, and items requiring author or subject-
matter approval. For high-sensitivity text, show proposed changes without overwriting
the source unless the user explicitly requests an in-place edit.

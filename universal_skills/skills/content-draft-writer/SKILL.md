---
name: content-draft-writer
domain: content
skill_type: skill
description: >-
  Write a complete first draft from an approved outline, source packet, audience,
  and voice constraints while preserving claim-to-source traceability. Use when the
  structure and evidence are settled and a user needs prose ready for editorial
  review. Do not use for source research, substantive fact verification, final copy
  editing, or publication.
license: MIT
tags: [content, drafting, writing, editorial, citations]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---

# Content Draft Writer

Write one draft that follows the approved outline. Do not silently expand scope or
turn unresolved outline items into confident assertions.

## Inputs

Require the approved outline, audience, format, target length, voice guide, source
packet, and citation style. State any missing constraint before drafting.

## Drafting contract

- Preserve the outline's thesis and section intent unless a contradiction makes it
  impossible; flag that contradiction instead of redesigning the piece silently.
- Attach source identifiers to factual claims as they are drafted.
- Distinguish sourced fact, attributed opinion, analysis, and prediction.
- Use quotations only when supplied or verified, and keep attribution intact.
- Do not fabricate statistics, examples, testimonials, links, or citations.
- Match the requested audience knowledge, vocabulary, tone, format, and length.

## Steps

1. Confirm all required inputs are present: outline, audience, format, length, voice guide, source packet, citation style.
   Run `ls` on the supplied files. Verify that every missing item is stated to the user before drafting.
2. Draft each section in outline order, attaching source identifiers as you write.
   Verify that each factual sentence carries an ID found by `grep -c "\[S[0-9]*\]" draft.md` or the citation style in use.
3. Mark unresolved or weakly supported claims in place instead of asserting them.
   Run `grep -n "TOD[O]\|UNSOURCED" draft.md`. Verify that every flagged item also appears in the editorial ledger.
4. Check length and format against the target.
   Run `wc -w draft.md`. Verify that the count is within the requested range.
5. Append the editorial ledger and stop at the reviewable draft.
   Run `grep -n "^## " draft.md` to find the ledger. Verify that the ledger lists unresolved claims, deviations, missing assets, word count, and citation assumptions, and that nothing was published.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| A needed fact has no source in the packet | Source packet incomplete | Leave the claim out or flag it in the ledger; do not invent a statistic or citation |
| Outline sections conflict | Thesis and section intent contradict | Draft as outlined, record the contradiction in the ledger deviations, and ask for a revised outline |
| Draft exceeds target length | Scope grew during writing | Trim to the outline's section purposes and list cut material in the ledger |

## Output

Return the draft followed by a compact editorial ledger containing:

- Unresolved or weakly supported claims.
- Deviations from the outline and why they were necessary.
- Missing assets, links, permissions, or subject-matter review.
- Approximate word count and citation-style assumptions.

Stop at a reviewable first draft. Do not publish, schedule, or send it.

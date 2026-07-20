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
  version: '1.2.1'
  author: Genius
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

## Output

Return the draft followed by a compact editorial ledger containing:

- Unresolved or weakly supported claims.
- Deviations from the outline and why they were necessary.
- Missing assets, links, permissions, or subject-matter review.
- Approximate word count and citation-style assumptions.

Stop at a reviewable first draft. Do not publish, schedule, or send it.

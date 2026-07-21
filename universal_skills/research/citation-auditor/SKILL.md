---
name: citation-auditor
domain: research
skill_type: skill
description: >-
  Audit whether each citation is reachable, authoritative enough, correctly
  attributed, and actually supports the nearby claim, including qualifiers and
  freshness. Use when reviewing a sourced draft, research report, technical memo,
  or evidence table before relying on or publishing its claims. Do not use to invent
  replacement evidence or rewrite the document.
license: MIT
tags: [research, citations, evidence, fact-checking, provenance]
metadata:
  version: '1.2.1'
  author: Genius
---

# Citation Auditor

Evaluate claim-to-source support. Prefer primary, authoritative, and current sources
when the claim requires them; do not penalize a source merely for disagreeing with
the draft.

## Audit contract

- Enumerate factual claims and the citations attached to each claim.
- Retrieve the cited source when access is available. Mark inaccessible material as
  unverified rather than guessing from a title or snippet.
- Compare the full claim—including scope, population, date, quantity, causality, and
  qualifiers—with what the source supports.
- Distinguish direct support, reasonable inference, partial support, contradiction,
  and no support.
- Check author or institution, publication date, version, methodology, conflicts,
  retractions or corrections, and whether a more primary source is required.
- Detect citation laundering, circular sourcing, quote distortion, broken anchors,
  and one citation being stretched across unrelated claims.

## Output

Return a table with claim ID, claim text, citation, accessibility, support status,
source-quality note, freshness, and required correction. End with counts by status
and a blocker list. Keep replacement-source suggestions separate and clearly labeled;
do not present an unreviewed replacement as verified support.

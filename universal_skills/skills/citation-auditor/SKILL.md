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
  version: '1.6.2'
  author: Knuckles-Team
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

## Steps

1. Enumerate every factual claim with its attached citation into a working list.
   Run `grep -nE '\[[0-9]+\]|https?://' draft.md` to locate citation markers. Verify that each claim has an ID and at least one citation, or is marked uncited.
2. Retrieve each cited source and mark it reachable or unverified.
   Fetch it with `curl -sIL -o /dev/null -w '%{http_code}' <url>` or the `WebFetch` tool. Verify that every URL has a recorded status and that inaccessible sources are labeled unverified, never guessed from a title.
3. Compare each full claim with what the source says: scope, date, quantity, causality, qualifiers.
   Use `grep -n -i '<key phrase>'` on the fetched text to find the supporting passage. Verify that each claim has one status: direct support, inference, partial, contradiction, or no support.
4. Check source quality and freshness: author or institution, date, version, corrections, and whether a more primary source is required.
   Run `grep -c '|' audit.md` on the draft table. Verify that each row carries a source-quality note and a freshness value.
5. Emit the audit table with counts by status and the blocker list, as in the Output section.
   Run `grep -c 'no support' audit.md` to confirm the counts. Verify that the counts sum to the number of claims and that replacement suggestions are labeled unreviewed.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Source returns 403, 404, or a paywall | Link rot or access control blocks retrieval | Mark the citation unverified, try the archived copy via `curl -sL https://archive.org/wait/<url>`, and list it as a blocker if still unreachable |
| Claim is supported only by an abstract or snippet | Full text unavailable | Record support as partial, quote the visible text only, and ask the author for the full source |
| Several claims share one citation | Citation stretched across unrelated claims | Split the claims, audit each against the specific passage, and flag laundering where the passage is absent |

## Output

Return a table with claim ID, claim text, citation, accessibility, support status,
source-quality note, freshness, and required correction. End with counts by status
and a blocker list. Keep replacement-source suggestions separate and clearly labeled;
do not present an unreviewed replacement as verified support.

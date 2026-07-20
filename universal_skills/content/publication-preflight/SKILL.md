---
name: publication-preflight
domain: content
skill_type: skill
description: >-
  Perform a read-only final readiness check on a publication artifact and return a
  pass, warning, or block decision with evidence. Use when edited content is about
  to be published, scheduled, sent, uploaded, or handed off and needs checks for
  completeness, links, citations, metadata, accessibility, rights, and approvals.
  Do not use to publish or silently repair the artifact.
license: MIT
tags: [content, publishing, quality-gate, accessibility, rights]
metadata:
  version: '1.2.1'
  author: Genius
---

# Publication Preflight

Inspect the final artifact without mutating it or triggering any external publication action.

## Gate criteria

Check only criteria relevant to the artifact and channel:

- Required sections, assets, metadata, dates, owners, and calls to action are present.
- Links resolve to the intended destination and citations are syntactically complete.
- Images, audio, video, tables, and interactive elements have appropriate accessible alternatives.
- Rights, licenses, releases, attribution, privacy, and confidential-information reviews are recorded.
- Channel-specific rendering, length, dimensions, encoding, and file-format constraints are met.
- Named reviewers and publication approval are explicit; draft markers and unresolved blockers are absent.
- Sending, posting, uploading, or scheduling targets match the user's stated destination.

Do not infer legal clearance, consent, or approval from silence.

## Output contract

Return an overall `PASS`, `WARN`, or `BLOCK`, then list each check with status,
evidence location, and the smallest corrective action. A warning must explain why
publication can still proceed; a blocker must identify the missing evidence or approval.
Never perform the publication action as part of this skill.

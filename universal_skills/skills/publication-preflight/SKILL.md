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
  version: '1.7.0'
  author: Knuckles-Team
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

## Steps

1. Identify the artifact, channel and destination from the request. Verify with `ls -l <artifact>` that the file exists and is readable.
2. Inspect the artifact against the gate criteria above. Verify with `grep -rniE "TOD[O]|DRAFT|lorem ipsum|FIXME" <artifact>` that no draft markers remain.
3. Check every link and citation. Verify with `grep -oE "https?://[^ )\"]+" <artifact>` that each URL is listed and each resolves to the intended destination.
4. Confirm rights, approvals and accessibility records with `grep -niE "license|credit|approved|alt=" <artifact>`. Verify that each has explicit evidence and no approval is inferred from silence.
5. Return the `PASS`, `WARN` or `BLOCK` decision as specified in the output contract. Verify that each check lists status, evidence and the smallest corrective action.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Link cannot be checked | Network access blocked or a login wall | Mark the check WARN with the URL listed and ask the owner to confirm manually |
| No approval evidence | Approval was not recorded in the artifact or request | Return BLOCK naming the missing approver and ask for explicit sign-off |
| Artifact changed during review | The file was edited after inspection | Rerun the checks on the latest version and report its modified time |

## Output contract

Return an overall `PASS`, `WARN`, or `BLOCK`, then list each check with status,
evidence location, and the smallest corrective action. A warning must explain why
publication can still proceed; a blocker must identify the missing evidence or approval.
Never perform the publication action as part of this skill.

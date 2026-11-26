---
name: skill-friction
description: >-
  File a friction report about a skill that misled you or cost you effort. Use
  when a skill step failed, was unclear, was out of date or asked for something
  that was not possible. One report holds one friction. A report never blocks
  the task.
license: MIT
metadata:
  version: '1.6.2'
  spec_digest: 'f7ad243703ac3b681e621aca58043d36db93dc9e234ac54bfcc9f7473094c475'
  domain: development
  skill_type: skill
  tier: always-on
  tags: [skills, friction, feedback, always-on]
---

# Report skill friction

A skill improves when the agents that use it say where it failed. This skill shows how to file the report.

<!-- spec:begin -->
## Goal

File one friction report when a skill misled you or cost you effort, then continue the task.

## Steps

1. Record what you tried, what you expected and what happened.
   - Run: `write the three facts in one short note`
   - Verify: The note names the skill step, the expected result and the actual result.
2. Add the fix when you know it.
   - Run: `write the change that would have helped in one sentence`
   - Verify: The fix names one change, or the note says that you do not know a fix.
3. Call the report operation with the skill ref and version.
   - Run: `skills.friction.report`
   - Verify: The answer returns a report id.
4. Continue the task.
   - Run: `continue the task with the skill as it is`
   - Verify: The task output does not wait for the report.

## Outputs

- One friction report for each friction you met.
- The report id in the final answer.

## Tool actions

Required:
- `skills.friction.report`

Forbidden:
- `skills.friction.transition`

## Error recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 1 fails | The check did not hold: The note names the skill step, the expected result and the actual result | Stop and report the state "no friction" if you cannot name the skill step. |
| Step 2 fails | The check did not hold: The fix names one change, or the note says that you do not know a fix | Leave the fix empty and say that you do not know one. |
| Step 3 fails | The check did not hold: The answer returns a report id | Read the refusal code in the table below and apply its recovery. Report the code if no recovery fits. |
| Step 4 fails | The check did not hold: The task output does not wait for the report | Report the blocked step in the final answer and stop. |
<!-- spec:end -->

## Rules

- One report holds one friction. File a second report for a second friction.
- A report never blocks the task. Continue after you file it.
- Never call `skills.friction.transition`. Reviewers move reports, not authors.
- Write what happened. Do not copy prompts, secrets or user data into the report.

## Refusal codes

| Failure | Cause | Recovery |
| --- | --- | --- |
| `FRICTION_SKILL_UNKNOWN` | The skill ref is not a published revision. | Use the skill ref and version from the skill header and file the report again. |
| `FRICTION_TRANSITION_ILLEGAL` | A state move is not allowed. | Stop. You must not move a report. Report the id. |
| `FRICTION_EVIDENCE_REQUIRED` | A move came without its evidence ref. | Stop. You must not move a report. Report the id. |
| `FRICTION_APPROVAL_ROLE_REQUIRED` | You tried to approve without the approve grant. | Stop. Leave approval to a reviewer. |
| `FRICTION_TEXT_TOO_LARGE` | The note is too long. | Cut the note to the three facts and file the report again. |

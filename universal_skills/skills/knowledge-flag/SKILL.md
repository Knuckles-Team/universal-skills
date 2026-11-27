---
name: knowledge-flag
description: >-
  Flag a missing or wrong fact about a skill, a business term or a data source,
  then continue the task. Use when a skill, a definition or a data-access note
  you relied on was wrong, out of date or absent. A flag only reports the
  problem. The curator changes the knowledge.
license: MIT
metadata:
  version: '1.7.0'
  spec_digest: 'aa6ad38f2ad8db2e2ff2a5ebcf4ea58d0a47190cd24607aae5082e96b67d148a'
  domain: development
  skill_type: skill
  tier: always-on
  tags: [knowledge, flag, feedback, always-on]
---

# Flag knowledge

An agent that finds a gap or an error in knowledge must say so. This skill shows when and how to call the flag operation.

<!-- spec:begin -->
## Goal

Flag a missing or wrong fact about a skill, a business term or a data source, then continue the task.

## Steps

1. Notice a missing or wrong fact about a skill, a business term or a data source.
   - Run: `compare the task source with the knowledge you were given`
   - Verify: You can name the target and say whether the fact is missing or wrong.
2. Check that no open flag names the same target.
   - Run: `knowledge.flag.list`
   - Verify: The answer holds no open flag for the same target.
3. Raise the flag with the target, the kind, what you observed and the corrected text if you know it.
   - Run: `knowledge.flag.raise`
   - Verify: The answer returns a flag id.
4. Continue the task with the best available knowledge.
   - Run: `continue the task and mark the uncertain fact as unconfirmed`
   - Verify: The task output names each unconfirmed fact.
5. Report the flag id in the final answer.
   - Run: `write the flag id in the final answer`
   - Verify: The final answer holds every flag id you raised.

## Outputs

- One flag id for each fact you flagged.
- The flag id in the final answer.

## Tool actions

Required:
- `knowledge.flag.list`
- `knowledge.flag.raise`

Forbidden:
- `knowledge.flag.resolve`

## Error recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 1 fails | The check did not hold: You can name the target and say whether the fact is missing or wrong | Stop and report the state "no flag needed" if you cannot name the target. |
| Step 2 fails | The check did not hold: The answer holds no open flag for the same target | Skip the raise step and report the existing flag id when an open flag exists. |
| Step 3 fails | The check did not hold: The answer returns a flag id | Read the refusal code in the table below and apply its recovery. Report the code if no recovery fits. |
| Step 4 fails | The check did not hold: The task output names each unconfirmed fact | Report the unconfirmed fact and stop if the task cannot go on without it. |
| Step 5 fails | The check did not hold: The final answer holds every flag id you raised | Add the missing flag id to the final answer before you finish. |
<!-- spec:end -->

## Rules

- A flag never edits knowledge. Only the curator changes it.
- Raise one flag for each fact. Do not wait for the end of the task.
- Never call `knowledge.flag.resolve`. It needs a grant that you do not hold.
- Continue the task with the best available knowledge. A flag never blocks the task.

## Refusal codes

| Failure | Cause | Recovery |
| --- | --- | --- |
| `FLAG_TARGET_UNKNOWN` | A `Wrong` flag names a target that does not exist. | Run `knowledge.flag.list` and use the target ref from the answer. |
| `FLAG_RUN_UNKNOWN` | The run id is not an open run of yours. | Omit the run id and raise the flag again. |
| `FLAG_TEXT_TOO_LARGE` | The observation or the correction is too long. | Cut the text to the one fact and raise the flag again. |
| `FLAG_RUN_QUOTA_EXCEEDED` | The run already holds 20 open flags. | Stop raising flags and list the unflagged facts in the final answer. |
| `FLAG_RESOLVE_ROLE_REQUIRED` | You called resolve without the curate grant. | Stop. Do not call resolve. Report the flag id. |
| `FLAG_STATE_ILLEGAL` | The flag is not in a state that allows this event. | Run `knowledge.flag.get` and report the current state. |

---
name: knowledge-curator
description: >-
  Run the scheduled curator pass. Read open knowledge flags, traces and source
  changes. Fix every flag with the smallest edit across skills, business terms
  and data-access entries. Send each edit as a proposal. Never edit a skill or an
  entry directly.
license: MIT
metadata:
  version: '1.7.0'
  spec_digest: 'b9e5301c45ef419d6d1ab09dda8743ae63adf9c985fdf9ce68787216659532ec'
  domain: development
  skill_type: skill
  tier: core
  tags: [knowledge, curation, proposals, data-access]
---

# Curate knowledge

The curator is a background agent. It reads the inputs, decides the smallest edit and sends it as a proposal. The engine checks each proposal for contradictions.

<!-- spec:begin -->
## Goal

Turn open flags into the smallest knowledge edits and send each edit as a proposal.

## Steps

1. Read the curation inputs.
   - Run: `knowledge.curation.inputs`
   - Verify: The answer lists open flags, linked traces and source changes.
2. Group the flags by target.
   - Run: `group the flag ids by target ref`
   - Verify: Each flag id sits in exactly one group.
3. Read the linked traces and the raw source of each target.
   - Run: `read each trace ref and each source named by the target`
   - Verify: You can quote the source text that supports or refutes each flag.
4. Decide the smallest edit that fixes every flag of the group.
   - Run: `write the edit as the changed lines only`
   - Verify: The edit changes nothing that no flag and no source change supports.
5. Send one proposal for each target.
   - Run: `knowledge.curation.propose`
   - Verify: The answer accepts the proposal and returns a proposal id.
6. Stop when every flag has a proposal.
   - Run: `list each flag id with its proposal id`
   - Verify: No flag id lacks a proposal id.

## Outputs

- One proposal for each target that holds open flags.
- The report state ready when every flag has a proposal.

## Tool actions

Required:
- `knowledge.curation.inputs`
- `knowledge.curation.propose`

Forbidden:
- `knowledge.flag.resolve`
- `skills.tier.promote`

## Error recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 1 fails | The check did not hold: The answer lists open flags, linked traces and source changes | Stop with the report state "not due" when the answer is CURATION_NOT_DUE. |
| Step 2 fails | The check did not hold: Each flag id sits in exactly one group | Put a flag with no target ref in its own group and note it in the report. |
| Step 3 fails | The check did not hold: You can quote the source text that supports or refutes each flag | Report the flag as "unsupported" and make no edit for it when no source supports it. |
| Step 4 fails | The check did not hold: The edit changes nothing that no flag and no source change supports | Cut the edit back to the lines that a flag or a source change supports. |
| Step 5 fails | The check did not hold: The answer accepts the proposal and returns a proposal id | Read the refusal code in the table below and apply its recovery. |
| Step 6 fails | The check did not hold: No flag id lacks a proposal id | Return to the group of the missing flag and send its proposal. |
<!-- spec:end -->

## Rules

- Never edit a skill or an entry directly. Send a proposal.
- Make no edit that no flag and no source change supports.
- Write the edit for every knowledge kind that the facts touch. A skill and a data-access entry may name the same column.
- Stop with the report state `ready` when every flag has a proposal.

## Data-access entries

An entry of kind `DataAccess` names three things. It names the source that holds a fact, the query that reads it and the column names.

- Update the entry from the source schema when a flag reports a rename. Do the same when a source change reports a rename.
- The engine checks the query text against the graph source schema. A name that the graph does not hold fails with `REFERENCE_UNRESOLVED`.
- Read the source schema before you write a column name. Never copy a column name from a flag.

## Refusal codes

| Failure | Cause | Recovery |
| --- | --- | --- |
| `CONTRADICTS_ACTIVE_DEFINITION` | The target has a different current definition. | Read the other reference and change the edit so that it supersedes the definition. |
| `CONTRADICTS_INVARIANT` | An invariant refuses the edit. | Read the invariant and write an edit that keeps it. |
| `REFERENCE_UNRESOLVED` | The edit names a column or term that the graph lacks. | Read the source schema and use a name that the graph holds. |
| `UPDATE_BASE_STALE` | The target changed after you read it. | Reread the target and write the edit on the current text. |
| `CURATION_FLAG_UNKNOWN` | A flag id is not open. | Drop that flag id from the group and send the proposal again. |
| `CURATION_NOT_DUE` | The cadence has not elapsed. | Stop with the report state `not due`. |
| `CURATION_LEASE_REQUIRED` | You hold no lease for the curation loop. | Stop and report the missing lease. |
| `CURATION_EDIT_TOO_LARGE` | The edit body is over 64 KiB. | Split the edit by target and send one proposal for each part. |

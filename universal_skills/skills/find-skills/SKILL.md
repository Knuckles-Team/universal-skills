---
name: find-skills
description: >-
  Find skills for a task and rank them by quality score and by peer use. Use
  when a person asks which skill to use, when no loaded skill fits the task, or
  when you need to compare skills. It lists skills and install commands. It
  installs nothing by itself.
license: MIT
metadata:
  version: '1.6.2'
  spec_digest: 'f2638cc85d979af47b7568478dd0cf86cb715fef4fd6f5c37cce912b73d9590a'
  domain: development
  skill_type: skill
  tier: core
  tags: [skills, discovery, ranking, peers]
---

# Find skills

This skill calls the served discovery operations and shows ranked results. It never installs a skill.

<!-- spec:begin -->
## Goal

Find the skills that fit a task and rank them by quality and by peer use.

## Steps

1. Describe the task in one sentence.
   - Run: `write one sentence that names the work and the system`
   - Verify: The sentence names one task and holds no list of tasks.
2. Search for skills that fit the sentence.
   - Run: `skills.find`
   - Verify: The answer lists skills with a quality score and an eval count.
3. Read the quality score and the eval count of each result.
   - Run: `compare the score and the eval count of each result`
   - Verify: Each result in your list shows both numbers.
4. Ask for the skills that peers use.
   - Run: `skills.peers.recommend`
   - Verify: The answer lists peer skills, or it returns PEER_COHORT_TOO_SMALL.
5. Report at most five skills.
   - Run: `write the table of skill, tier, quality score and install command`
   - Verify: The table has five rows or fewer and each row has all four fields.

## Outputs

- At most five skills with name, tier, quality score and install command.

## Tool actions

Required:
- `skills.find`
- `skills.peers.recommend`

Forbidden:
- `skills.tier.promote`

## Error recovery

| Failure | Cause | Recovery |
| --- | --- | --- |
| Step 1 fails | The check did not hold: The sentence names one task and holds no list of tasks | Split the task and run this skill once for each part. |
| Step 2 fails | The check did not hold: The answer lists skills with a quality score and an eval count | Use a shorter sentence with the main noun and search again with that input. |
| Step 3 fails | The check did not hold: Each result in your list shows both numbers | Mark a result with no eval runs as unproven and rank it last. |
| Step 4 fails | The check did not hold: The answer lists peer skills, or it returns PEER_COHORT_TOO_SMALL | Report that no peer list exists when the answer is PEER_COHORT_TOO_SMALL. |
| Step 5 fails | The check did not hold: The table has five rows or fewer and each row has all four fields | Cut the list to the five best and add the missing field from the search answer. |
<!-- spec:end -->

## Rules

- Prefer a skill with eval runs over a skill without eval runs.
- A `PEER_COHORT_TOO_SMALL` answer means no peer list exists. Do not guess one.
- Show the install command of the door. Do not run it.
- Never call `skills.tier.promote`. Promotion is a review step.

## Refusal codes

| Failure | Cause | Recovery |
| --- | --- | --- |
| `PEER_COHORT_TOO_SMALL` | Too few peers use skills like these. | Report that no peer list exists and rank by quality score only. |
| `POLICY_DENIED` | You lack the telemetry read grant. | Stop and report the missing grant. |
| `UNAVAILABLE` | The engine did not answer. | Stop and report that discovery is unavailable. |

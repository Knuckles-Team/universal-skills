# Contract: the delivery skill for one assignment run

Provider: universal-skills US-CONTENT-R004
Consumer: meristem MERISTEM-SCM-R012

A delivery assignment run of meristem loads the skill. MERISTEM-SCM-R011 is the task run it extends. The run reports to the engine delivery records (MEDULLA-SDLC-R019.7).

## Wire shape

- Resource: `skill://spec-row-delivery/SKILL.md`, read through arbora.
- Content: the ordered steps, the six report states `progress`, `waiting`, `ready`, `blocked`, `failed` and `dropped`, the review-thread rules and four prohibitions.

## Refusal codes

- An absent resource leaves the run without the procedure. The run reports `blocked` with the reason `delivery_skill_missing`.

## Authoritative types

- `universal_skills/skills/spec-row-delivery/SKILL.md`.
- `meristem/harness/delivery_run.py` of MERISTEM-SCM-R012.

## Test vectors

- `tests/test_spec_row_delivery_skill.py`.

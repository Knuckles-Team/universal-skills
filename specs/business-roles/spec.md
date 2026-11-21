# US-BUSINESS-ROLES — Business role workflow skills

Owner: universal-skills. Cross-repo IDs: `ARBORA-IDENTITY-R019`.

References: [ARBORA-IDENTITY](https://github.com/Knuckles-Team/arbora/blob/main/specs/identity-access/spec.md)

## Purpose and user stories

A small business runs on role agents that use a small local model. Each role needs workflow skills that work for any business. A skill reads the business profile from the knowledge graph. A person approves the gated steps.

## User scenarios and testing

### User Story 1 - Run a routine duty end to end (Priority: P1)

An owner wants a routine duty done, such as order to cash or month-end close. The role agent runs the matching skill. The skill composes atomic connector skills and returns one record of done items and exceptions.

**Acceptance scenarios**

1. Given a paid order, When the agent runs `order-to-cash`, Then the ERP holds a sales order and a payment entry, and one reconciliation record lists any mismatch.
2. Given a closed period, When the agent runs `month-end-close`, Then the record lists unmatched payouts and fees and no closing entry is posted.

### User Story 2 - Stop at the human gate (Priority: P1)

A skill must stop where a person decides. Legal filing, money movement, publishing and production release each wait for a grant.

**Acceptance scenarios**

1. Given a prepared return worksheet, When the skill reaches filing, Then it requests approval and files nothing without a grant.
2. Given a draft purchase order, When the skill reaches submission, Then it requests the money gate and submits nothing without a grant.

### User Story 3 - Work for any business (Priority: P1)

Two businesses with different profiles use the same skill. Each run reads its own profile. The skill text names neither business.

**Acceptance scenarios**

1. Given two fixture profiles, When one skill runs on each, Then the outputs use each profile's values and the skill text is unchanged.

## Edge Cases

- A required profile field is absent: the skill stops and asks one question.
- An approval is denied: the skill records the denial and ends the run with no gated step done.
- A composed connector skill is not installed for the tenant: the skill reports the missing capability and stops.

## Assumptions

- The business profile is a graph record that a served read operation returns.
- Approvals are served by `ARBORA-IDENTITY-R019`.
- Connector skills named in `Composes` sections are published by their own repositories.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository, `git grep -n "workflow\|order\|reconcil\|tax\|digest" -- specs`. `US-SKILL-GRAPH-BUILDER` owns graph distillation and `US-WEB-RESEARCH` owns web skills. No spec owns business role workflow skills.

## Scope and interfaces

In scope: eleven workflow skills under `universal_skills/skills/` and their tests.

Out of scope: the business profile vocabulary and read operation, the approval service, and every connector tool. Each belongs to its owner.

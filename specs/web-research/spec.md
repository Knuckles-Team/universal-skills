# US-WEB-RESEARCH — Web research skills call the served operation

Owner: universal-skills. Cross-repo IDs: `ARBORA-OPS-R067`.

References: [ARBORA-OPS](https://github.com/Knuckles-Team/arbora/blob/main/specs/hosted-api-operations/spec.md)

## Purpose and user stories

A person asks an agent to research a topic on the web. The agent runs the `web-crawler` skill. The skill calls one served operation. The platform stores each chosen page as one Document with its source URL.

## User scenarios and testing

### User Story 1 - Research a topic on the web (Priority: P1)

A person asks an agent to research a topic. The agent runs the web-crawler skill, which calls one served operation, so that each chosen page is stored as one Document with its source URL.

**Acceptance scenarios**

1. Given a query, When the agent runs the skill, Then one `research.web` call carries the mapped query, URLs and backend, and the skill prints each Document ID with its citation.
2. Given one URL, When the agent runs web-fetch, Then it sends one `research.web` call with that URL and `max_pages` 1.

### User Story 2 - Refuse without a local fallback (Priority: P1)

When the platform refuses a request, the skill reports the refusal and does nothing else.

**Acceptance scenarios**

1. Given a refused call, When the skill finishes, Then it prints the refusal code, exits with status 2 and makes no other network call.

## Edge Cases

- The arbora endpoint is unreachable: the skill reports the transport failure and exits non-zero without a local fetch.
- Both `--query` and `--urls` are given: both map to the operation arguments.
- An unknown backend name is passed through and the operation decides the refusal.

## Assumptions

- Arbora serves `research.web` as described by `ARBORA-OPS-R067`.
- Search, selection, fetch and ingest belong to the owners that `ARBORA-OPS-R067` composes.
- The web-search skill stays out of scope.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. The only spec is `US-PAGES`, which owns published documentation. No spec owns the web skills.

## Scope and interfaces

In scope: the `web-crawler` and `web-fetch` skill scripts and their `SKILL.md` files.

Out of scope: the `web-search` skill. Search, selection, fetch and ingest belong to the owners that `ARBORA-OPS-R067` composes.

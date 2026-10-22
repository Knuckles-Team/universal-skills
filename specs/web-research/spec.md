# US-WEB-RESEARCH — Web research skills call the served operation

Owner: universal-skills. Cross-repo IDs: `ARBORA-OPS-R067`.

References: [ARBORA-OPS](https://github.com/Knuckles-Team/arbora/blob/main/specs/hosted-api-operations/spec.md)

## Purpose and user stories

A person asks an agent to research a topic on the web. The agent runs the `web-crawler` skill. The skill calls one served operation. The platform stores each chosen page as one Document with its source URL.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. The only spec is `US-PAGES`, which owns published documentation. No spec owns the web skills.

## Scope and interfaces

In scope: the `web-crawler` and `web-fetch` skill scripts and their `SKILL.md` files.

Out of scope: the `web-search` skill. Search, selection, fetch and ingest belong to the owners that `ARBORA-OPS-R067` composes.

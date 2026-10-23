# US-MCP-BUILDER — The mcp-builder scaffold meets the SDK centralized-capability rules

Owner: universal-skills. Cross-repo IDs: `SDK-CENTRALIZED-CAPABILITIES-R001`, `SDK-CENTRALIZED-CAPABILITIES-R008`, `SDK-CENTRALIZED-CAPABILITIES-R009`, `SDK-CENTRALIZED-CAPABILITIES-R015`, `SDK-CENTRALIZED-CAPABILITIES-R016`, `SDK-CENTRALIZED-CAPABILITIES-R030`, `SDK-CENTRALIZED-CAPABILITIES-R040`, `SDK-CONNECTOR-CONTROL-R071`.

References: [SDK-CENTRALIZED-CAPABILITIES](https://github.com/Knuckles-Team/agent-connector-sdk/blob/main/specs/centralized-capabilities/spec.md)

## Purpose and user stories

A maintainer runs the `mcp-builder` scaffold to start a connector. The generated connector must already meet every SDK centralized-capability rule. The 2026-10-22 audit of 79 connectors found own HTTP clients, copied retries, `gql` wrappers, hand-parsed secret references, connector-name literals, stale bumpversion entries and failing hooks. Each came from a connector that started without the rule.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. `US-PAGES` owns published documentation and `US-WEB-RESEARCH` owns the web skills. No spec owns the connector scaffold.

## Scope and interfaces

In scope: `universal_skills/agent-tools/mcp-builder/` (`SKILL.md`, `scripts/scaffold_package.py`, its templates and `scripts/check_connector_contract.py`).

Out of scope: the SDK capabilities themselves (SDK owns them), the pipelines hook bodies (pipelines owns them), and migrating existing connectors (each connector repository owns its own fix).

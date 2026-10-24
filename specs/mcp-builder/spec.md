# US-MCP-BUILDER — The mcp-builder scaffold builds connectors on SDK components

Owner: universal-skills. Cross-repo IDs: `SDK-CONNECTOR-CONTROL-R019.1`, `SDK-CONNECTOR-CONTROL-R028.4`, `SDK-QUALITY-RELEASE-R005.1`, `SDK-SOURCE-INGEST-R004.29`.

References: [SDK-CENTRALIZED-CAPABILITIES](https://github.com/Knuckles-Team/agent-connector-sdk/blob/main/specs/centralized-capabilities/spec.md)

## Purpose and user stories

A maintainer runs the `mcp-builder` scaffold to start a connector. The generated connector holds only what is specific to one external system and uses SDK components for the server, tests, version lookup and auth. The shared pipelines own gates, container files and release.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository. `US-PAGES` owns published documentation and `US-WEB-RESEARCH` owns the web skills. No spec owns the connector scaffold.

## Scope and interfaces

In scope: `universal_skills/skills/mcp-builder/` (`SKILL.md`, `scripts/scaffold_connector.py`).

Out of scope: the SDK capabilities themselves (SDK owns them), the pipelines hook bodies (pipelines owns them), and migrating existing connectors (each connector repository owns its own fix).

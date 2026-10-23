# CONN-WGER-AGENT-SDK-CENTRALIZATION — Shared SDK capabilities in wger-agent

**Owner:** wger-agent.

See [`requirements.md`](requirements.md) for each row and [`status.json`](status.json) for its generated state.

## Purpose

wger-agent must use the agent-connector-sdk capability for each concern the SDK centralizes. A connector copy of a centralized capability splits policy across the fleet.

## Why a new spec

Search: `git grep -n "SDK" -- specs` found no row that owns SDK capability use in wger-agent. The SDK index spec `SDK-CENTRALIZED-CAPABILITIES` owns the capabilities. This spec owns the connector side of each one.

## Requirements

- `CONN-WGER-AGENT-SDK-CENTRALIZATION-R001`: Requests use the governed SDK client.
- `CONN-WGER-AGENT-SDK-CENTRALIZATION-R002`: SDK floor and dependency set.
- `CONN-WGER-AGENT-SDK-CENTRALIZATION-R003`: Production wiring and hot path.

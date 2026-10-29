# CONN-CADDY-MCP-SDK-CENTRALIZATION — Shared SDK capabilities in caddy-mcp

**Owner:** caddy-mcp.

See [`requirements.md`](requirements.md) for each row and [`status.json`](status.json) for its generated state.

## Purpose

caddy-mcp must use the agent-connector-sdk capability for each concern the SDK centralizes. A connector copy of a centralized capability splits policy across the fleet.

## Why a new spec

Search: `git grep -n "SDK" -- specs` found no row that owns SDK capability use in caddy-mcp. The SDK index spec `SCION-CENTRALIZED-CAPABILITIES` owns the capabilities. This spec owns the connector side of each one.

## Requirements

- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001`: Requests use the governed SDK client.
- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002`: SDK floor and dependency set.
- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003`: Production wiring and hot path.

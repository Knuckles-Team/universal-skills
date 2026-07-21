---
name: eunomia-policy-manager
domain: infrastructure
skill_type: skill
description: >-
  Manage Eunomia authorization policies for the MCP server fleet. Lists,
  creates, pushes, and deletes policies on the centralized Eunomia remote
  authorization server. Use when the user says "list policies", "show
  eunomia policies", "push policies", "create mcp policy", "delete policy",
  "audit authorization", "eunomia status", or needs to inspect or modify
  the authorization rules governing MCP tool execution. Do NOT use for
  Eunomia server deployment — use infrastructure-orchestrator for that.
  Do NOT use for Keycloak SSO or OpenBao secrets — use dedicated skills.
license: MIT
tags: [eunomia, authorization, policies, mcp, security, governance]
metadata:
  version: '1.2.1'
  author: Genius
---

# Eunomia Policy Manager Skill

Atomic operations for managing authorization policies on the centralized Eunomia remote server that governs MCP tool execution.

## Prerequisites

- **Eunomia Server** connection resolved from an AgentConfig connection profile.
- Python 3.10+ with `eunomia-sdk` installed (`pip install eunomia-sdk`).
- Policy JSON files in `services/eunomia/policies/` (for push operations).

## Configuration

| Variable | Default | Description |
|---|---|---|
| `EUNOMIA_ENDPOINT` | required at runtime | URL resolved from the configured Eunomia connection profile |
| `POLICY_DIR` | `services/eunomia/policies/` | Directory containing per-service policy JSON files |

Resolve the connection through AgentConfig and pass its runtime value with
`--endpoint`; never commit it. Override the policy source with `--policy-dir`.

## Operations

### 1. List Policies

Retrieve and display all registered policies from the Eunomia server:

```bash
python scripts/list_policies.py
```

The script:
1. Connects to the Eunomia server at `EUNOMIA_ENDPOINT`.
2. Calls `client.get_policies()` to retrieve all registered policies.
3. Prints each policy's name, description, default effect, and individual rules with their actions.

**Example output:**
```
Successfully retrieved 5 policies:
- caddy-mcp-policy: Authorization policy for caddy-mcp MCP server (default: allow)
  * Rule 'unrestricted-access': allow for actions ['list', 'execute']
```

### 2. Create Policy Files

Generate per-service policy JSON files for all known MCP servers:

```bash
python scripts/create_policies.py
```

The script:
1. Iterates over a predefined list of MCP service names.
2. Generates a policy JSON file per service in `POLICY_DIR` with:
   - `default_effect: allow` (audit-mode, permissive by default)
   - A single `unrestricted-access` rule allowing `list` and `execute` actions
3. Writes each file as `{service-name}.json`.

### 3. Push Policies to Server

Upload all local policy files to the remote Eunomia server:

```bash
python scripts/push_policies.py
```

The script:
1. Scans `POLICY_DIR` for `*.json` files.
2. Validates each against the `eunomia_sdk.client.schemas.Policy` Pydantic model.
3. Deletes any existing policy with the same name (idempotent upsert).
4. Creates the policy on the remote server via `client.create_policy()`.

## Policy JSON Schema

Each policy file follows this structure:

```json
{
  "version": "1.0",
  "name": "{service-name}-policy",
  "description": "Authorization policy for {service-name} MCP server",
  "default_effect": "allow",
  "rules": [
    {
      "name": "unrestricted-access",
      "description": "All principals can list and execute tools, resources, and prompts",
      "effect": "allow",
      "principal_conditions": [],
      "resource_conditions": [],
      "actions": ["list", "execute"]
    }
  ]
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `version` | string | Policy schema version (always `"1.0"`) |
| `name` | string | Unique policy name (convention: `{service}-policy`) |
| `default_effect` | `allow` or `deny` | Fallback when no rule matches |
| `rules[].effect` | `allow` or `deny` | What to do when this rule matches |
| `rules[].actions` | list | MCP actions: `list`, `execute` |
| `rules[].principal_conditions` | list | Filter by caller identity (empty = any) |
| `rules[].resource_conditions` | list | Filter by tool/resource name (empty = any) |

## Error Handling

- **Connection refused**: run the AgentConfig/doctor connection check for the
  selected Eunomia profile; do not substitute a stored endpoint or disable TLS.
- **eunomia-sdk not installed**: Run `pip install eunomia-sdk`.
- **Invalid policy JSON**: The push script validates against Pydantic schemas and reports specific validation errors.
- **Policy already exists**: The push script deletes existing policies before re-creating (idempotent).

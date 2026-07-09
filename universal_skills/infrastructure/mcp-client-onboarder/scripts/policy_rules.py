#!/usr/bin/env python3
"""Eunomia rule generation + policy-file mutation for the MCP client onboarder.

The central multiplexer runs Eunomia **embedded** over a single policy file
(``eunomia_policy.json``): ``default_effect: deny``, a ``_base`` rule granting
every authenticated principal the discovery meta-tools, and one or more
per-client rules. Onboarding a client = generating its rule(s) from a profile
template and merging them into that file (idempotent: a re-onboard replaces the
client's prior rules). Resolution order is deny-by-default → _base allow → the
principal's allow rules.
"""

from __future__ import annotations

import json
from pathlib import Path

PROFILES = ("full-access", "read-only", "server-scoped", "role-based")


def server_prefix(server: str) -> str:
    """Tool-name prefix for a server. Uses the multiplexer's authoritative
    derivation when importable; otherwise treats the value as already a prefix."""
    try:
        from agent_utilities.mcp.multiplexer import get_server_prefix

        return get_server_prefix(server)
    except Exception:
        return server.split("-")[0] if "-" in server else server


def _principal(client_id: str) -> str:
    return f"agent:{client_id}"


def build_rules(
    client_id: str,
    profile: str,
    servers: list[str] | None = None,
    roles_map: dict[str, list[str]] | None = None,
    role: str | None = None,
) -> list[dict]:
    """Generate the Eunomia allow-rule(s) for one client under a profile."""
    principal = _principal(client_id)
    pc = [{"path": "uri", "operator": "equals", "value": principal}]

    def rule(name, actions, resource_conditions):
        return {
            "name": name,
            "description": f"{profile} access for {client_id} (mcp-client-onboarder).",
            "effect": "allow",
            "principal_conditions": pc,
            "resource_conditions": resource_conditions,
            "actions": actions,
        }

    if profile == "full-access":
        return [rule(f"{client_id}-full", ["list", "execute"], [])]
    if profile == "read-only":
        # Discover-only: list every tool but execute nothing (real tools).
        return [rule(f"{client_id}-readonly", ["list"], [])]
    if profile == "server-scoped":
        prefixes = [server_prefix(s) for s in (servers or [])]
        if not prefixes:
            raise ValueError("server-scoped requires --servers")
        # One rule per server prefix → the union (OR) of the named servers' tools.
        return [
            rule(
                f"{client_id}-srv-{p}",
                ["list", "execute"],
                [{"path": "attributes.name", "operator": "startswith", "value": f"{p}__"}],
            )
            for p in prefixes
        ]
    if profile == "role-based":
        if not role or not roles_map or role not in roles_map:
            raise ValueError(f"role-based requires --role in {list((roles_map or {}))}")
        prefixes = [server_prefix(s) for s in roles_map[role]]
        return [
            rule(
                f"{client_id}-role-{role}-{p}",
                ["list", "execute"],
                [{"path": "attributes.name", "operator": "startswith", "value": f"{p}__"}],
            )
            for p in prefixes
        ]
    raise ValueError(f"unknown profile '{profile}' (choose from {PROFILES})")


def _is_clients_rule(rule: dict, client_id: str) -> bool:
    """True if a rule belongs to this client (by principal or name prefix)."""
    principal = _principal(client_id)
    for cond in rule.get("principal_conditions", []):
        if cond.get("path") == "uri" and cond.get("value") == principal:
            return True
    return rule.get("name", "").startswith(f"{client_id}-")


def upsert_client_rules(policy_path: Path, client_id: str, rules: list[dict]) -> dict:
    """Replace a client's rules in the policy file (idempotent). Never touches
    ``_base`` or other principals. Returns the updated policy dict."""
    policy = json.loads(policy_path.read_text())
    kept = [
        r
        for r in policy.get("rules", [])
        if r.get("name") == "_base-meta-tools" or not _is_clients_rule(r, client_id)
    ]
    policy["rules"] = kept + rules
    policy_path.write_text(json.dumps(policy, indent=2) + "\n")
    return policy


def remove_client_rules(policy_path: Path, client_id: str) -> int:
    """Drop all of a client's rules from the policy file. Returns count removed."""
    policy = json.loads(policy_path.read_text())
    before = len(policy.get("rules", []))
    policy["rules"] = [
        r
        for r in policy.get("rules", [])
        if r.get("name") == "_base-meta-tools" or not _is_clients_rule(r, client_id)
    ]
    policy_path.write_text(json.dumps(policy, indent=2) + "\n")
    return before - len(policy["rules"])

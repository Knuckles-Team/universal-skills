#!/usr/bin/env python3
"""Generate per-service authorization policy JSON files for MCP servers.

Usage:
    python create_policies.py [--policy-dir DIR] [--services SVC1,SVC2,...]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Default set of known MCP services in the fleet
DEFAULT_SERVICES = [
    "archivebox-mcp",
    "arr-mcp",
    "audio-transcriber-mcp",
    "caddy-mcp",
    "container-manager-mcp",
    "documentdb-mcp",
    "erpnext-mcp",
    "genius-mcp",
    "github-mcp",
    "gitlab-mcp",
    "jellyfin-mcp",
    "keycloak-agent",
    "keycloak-mcp",
    "mealie-mcp",
    "media-downloader-mcp",
    "microsoft-mcp",
    "nextcloud-mcp",
    "openbao-mcp",
    "portainer-agent",
    "portainer-mcp",
    "repository-manager-mcp",
    "searxng-mcp",
    "servicenow-mcp",
    "systems-manager",
    "systems-manager-mcp",
    "technitium-dns-mcp",
    "tunnel-manager-mcp",
    "uptime-mcp",
    "vector-mcp",
    "wger-mcp",
]


def create_policy(service_name: str) -> dict:
    """Create a permissive (audit-mode) policy dict for a service."""
    return {
        "version": "1.0",
        "name": f"{service_name}-policy",
        "description": f"Authorization policy for {service_name} MCP server",
        "default_effect": "allow",
        "rules": [
            {
                "name": "unrestricted-access",
                "description": "All principals can list and execute tools, resources, and prompts",
                "effect": "allow",
                "principal_conditions": [],
                "resource_conditions": [],
                "actions": ["list", "execute"],
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Eunomia policy JSON files for MCP services."
    )
    parser.add_argument(
        "--policy-dir",
        default=os.environ.get("POLICY_DIR", "services/eunomia/policies"),
        help="Output directory for policy files (default: services/eunomia/policies)",
    )
    parser.add_argument(
        "--services",
        default=None,
        help="Comma-separated list of service names (default: all known MCP services)",
    )
    args = parser.parse_args()

    services = (
        [s.strip() for s in args.services.split(",")]
        if args.services
        else DEFAULT_SERVICES
    )

    os.makedirs(args.policy_dir, exist_ok=True)

    created = 0
    for svc in sorted(services):
        policy = create_policy(svc)
        filepath = os.path.join(args.policy_dir, f"{svc}.json")
        with open(filepath, "w") as f:
            json.dump(policy, f, indent=2)
            f.write("\n")
        print(f"  [created] {filepath}")
        created += 1

    print(f"\nGenerated {created} policy file(s) in {args.policy_dir}/")


if __name__ == "__main__":
    main()

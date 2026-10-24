#!/usr/bin/env python3
"""Onboard an MCP client to the central multiplexer in one shot (plan Phase 4).

Creates a Keycloak ``client_credentials`` client, generates its Eunomia rule(s)
from a profile template, and merges them into the multiplexer's embedded policy
file. Optionally stamps a TTL so the ephemeral reaper revokes it later.

    # full access, permanent
    onboard.py my-agent --profile full-access

    # read-only (discover but execute nothing)
    onboard.py auditor --profile read-only

    # only two servers' tools, expires in 24h
    onboard.py ci-bot --profile server-scoped --servers github-mcp,gitlab-mcp --ttl 24h

    # a named role (servers from roles.json)
    onboard.py oncall --profile role-based --role devops

After onboarding, retrieve the generated credential through the configured
secret-management workflow, then restart the multiplexer so its policy reloads.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keycloak_client as kc  # noqa: E402
import policy_rules as pr  # noqa: E402

_CONFIG_ROOT = Path(
    os.environ.get("AGENT_UTILITIES_CONFIG_DIR")
    or Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "agent-utilities"
)
_MULTIPLEXER_CONFIG = _CONFIG_ROOT / "mcp-multiplexer"
DEFAULT_POLICY = os.environ.get(
    "MCP_POLICY_FILE", str(_MULTIPLEXER_CONFIG / "eunomia_policy.json")
)
DEFAULT_EPHEMERAL = os.environ.get(
    "MCP_EPHEMERAL_FILE",
    str(_MULTIPLEXER_CONFIG / "ephemeral_clients.json"),
)
DEFAULT_ROLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "roles.json"
)

_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(s: str) -> int:
    unit = s[-1].lower()
    if unit not in _UNITS or not s[:-1].isdigit():
        raise ValueError(f"bad --ttl '{s}' (use e.g. 90m, 24h, 7d)")
    return int(s[:-1]) * _UNITS[unit]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("client_id")
    ap.add_argument("--profile", required=True, choices=pr.PROFILES)
    ap.add_argument("--servers", help="comma-separated servers (server-scoped)")
    ap.add_argument("--role", help="role name (role-based)")
    ap.add_argument("--ttl", help="ephemeral lifetime, e.g. 90m / 24h / 7d")
    ap.add_argument("--policy-file", default=DEFAULT_POLICY)
    ap.add_argument("--roles-file", default=DEFAULT_ROLES)
    ap.add_argument("--ephemeral-file", default=DEFAULT_EPHEMERAL)
    ap.add_argument(
        "--no-keycloak",
        action="store_true",
        help="policy only (skip Keycloak client creation)",
    )
    args = ap.parse_args()

    servers = [s.strip() for s in (args.servers or "").split(",") if s.strip()]
    roles_map = {}
    if os.path.isfile(args.roles_file):
        roles_map = json.loads(Path(args.roles_file).read_text())

    rules = pr.build_rules(
        args.client_id, args.profile, servers=servers, roles_map=roles_map, role=args.role
    )

    if not args.no_keycloak:
        if not kc.ADMIN_PASS:
            return _fail("Set KEYCLOAK_ADMIN_PASSWORD to create the Keycloak client.")
        token = kc.get_admin_token()
        kc.create_client(args.client_id, token)

    pr.upsert_client_rules(Path(args.policy_file), args.client_id, rules)

    if args.ttl:
        seconds = parse_duration(args.ttl)
        expiry = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
        eph_path = Path(args.ephemeral_file)
        eph = json.loads(eph_path.read_text()) if eph_path.exists() else {}
        eph[args.client_id] = {"expires_at": expiry, "profile": args.profile}
        pr.write_private_json(eph_path, eph)

    print(f"Onboarded configured client with {len(rules)} policy rule(s).")
    if not args.no_keycloak:
        print("  Client created; retrieve its credential through identity-provider admin tooling.")
    if args.ttl:
        print(f"  ephemeral: expires in {args.ttl} (run reap.py to revoke)")
    print("  NEXT: restart the mcp-multiplexer service so the embedded policy reloads.")
    return 0


def _fail(msg: str) -> int:
    print("ERROR: client onboarding failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

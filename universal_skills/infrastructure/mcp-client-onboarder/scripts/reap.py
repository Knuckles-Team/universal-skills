#!/usr/bin/env python3
"""Revoke expired ephemeral MCP clients (plan Phase 4 TTL reaper).

Eunomia has no native TTL, so ``onboard.py --ttl`` records an expiry in a sidecar
(``ephemeral_clients.json``). This reaper revokes everything past its expiry: it
removes the client's rules from the embedded policy file AND deletes its Keycloak
client. Run from cron / a daemon tick (e.g. hourly):

    KEYCLOAK_ADMIN_PASSWORD=… reap.py            # revoke expired
    reap.py --dry-run                            # report only

Restart the multiplexer afterwards if anything was revoked (the embedded PDP
reads the policy at boot).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keycloak_client as kc  # noqa: E402
import policy_rules as pr  # noqa: E402

DEFAULT_POLICY = os.environ.get(
    "MCP_POLICY_FILE", "/home/apps/workspace/services/mcp-multiplexer/eunomia_policy.json"
)
DEFAULT_EPHEMERAL = os.environ.get(
    "MCP_EPHEMERAL_FILE",
    "/home/apps/workspace/services/mcp-multiplexer/ephemeral_clients.json",
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--policy-file", default=DEFAULT_POLICY)
    ap.add_argument("--ephemeral-file", default=DEFAULT_EPHEMERAL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    eph_path = Path(args.ephemeral_file)
    if not eph_path.exists():
        print("no ephemeral clients tracked.")
        return 0
    eph = json.loads(eph_path.read_text())
    now = datetime.now(timezone.utc)

    expired = [
        cid
        for cid, meta in eph.items()
        if datetime.fromisoformat(meta["expires_at"]) <= now
    ]
    if not expired:
        print(f"nothing expired ({len(eph)} ephemeral client(s) still valid).")
        return 0

    token = None
    if not args.dry_run and kc.ADMIN_PASS:
        token = kc.get_admin_token()

    revoked = 0
    for cid in expired:
        if args.dry_run:
            print(f"  would revoke: {cid} (expired {eph[cid]['expires_at']})")
            continue
        n = pr.remove_client_rules(Path(args.policy_file), cid)
        deleted = kc.delete_client(cid, token) if token else False
        eph.pop(cid, None)
        revoked += 1
        print(f"  revoked {cid}: {n} policy rule(s) removed, keycloak={'yes' if deleted else 'no'}")

    if not args.dry_run:
        eph_path.write_text(json.dumps(eph, indent=2) + "\n")
        if revoked:
            print(f"revoked {revoked} client(s). RESTART the mcp-multiplexer to reload policy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

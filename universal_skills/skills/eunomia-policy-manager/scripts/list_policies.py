#!/usr/bin/env python3
"""List all authorization policies registered on the Eunomia remote server.

Usage:
    python list_policies.py [--endpoint URL]
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="List Eunomia authorization policies.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("EUNOMIA_ENDPOINT"),
        required=not bool(os.environ.get("EUNOMIA_ENDPOINT")),
        help="Eunomia server URL (or set EUNOMIA_ENDPOINT)",
    )
    args = parser.parse_args()

    try:
        from eunomia_sdk import EunomiaClient
    except ImportError:
        print(
            "Error: eunomia-sdk is not installed. Run: pip install eunomia-sdk",
            file=sys.stderr,
        )
        sys.exit(1)

    client = EunomiaClient(endpoint=args.endpoint)
    try:
        policies = client.get_policies()
    except Exception as e:
        print(f"Eunomia connection failed ({type(e).__name__})", file=sys.stderr)
        sys.exit(1)

    if not policies:
        print("No policies registered on the Eunomia server.")
        return

    print(f"Retrieved {len(policies)} policy(ies):\n")
    for p in policies:
        effect_str = getattr(p, "default_effect", "unknown")
        print(f"  📋 {p.name}")
        print(f"     Description : {p.description}")
        print(f"     Default     : {effect_str}")
        for r in p.rules:
            print(f"     ├─ Rule '{r.name}': {r.effect} → actions {r.actions}")
        print()


if __name__ == "__main__":
    main()

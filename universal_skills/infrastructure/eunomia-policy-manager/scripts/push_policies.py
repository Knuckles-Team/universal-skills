#!/usr/bin/env python3
"""Push local policy JSON files to the centralized Eunomia remote server.

Performs idempotent upserts: deletes any existing policy with the same name
before re-creating it, ensuring the remote server always reflects the local
policy directory state.

Usage:
    python push_policies.py [--endpoint URL] [--policy-dir DIR] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push Eunomia policy files to the remote server."
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("EUNOMIA_ENDPOINT"),
        required=not bool(os.environ.get("EUNOMIA_ENDPOINT")),
        help="Eunomia server URL (or set EUNOMIA_ENDPOINT)",
    )
    parser.add_argument(
        "--policy-dir",
        default=os.environ.get("POLICY_DIR", "services/eunomia/policies"),
        help="Directory containing policy JSON files (default: services/eunomia/policies)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print policies without pushing to the server.",
    )
    args = parser.parse_args()

    try:
        from eunomia_sdk import EunomiaClient
        from eunomia_sdk.client import schemas
    except ImportError:
        print(
            "Error: eunomia-sdk is not installed. Run: pip install eunomia-sdk",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isdir(args.policy_dir):
        print("Error: configured policy directory was not found", file=sys.stderr)
        sys.exit(1)

    client = EunomiaClient(endpoint=args.endpoint)

    json_files = sorted(f for f in os.listdir(args.policy_dir) if f.endswith(".json"))
    if not json_files:
        print("No JSON policy files found in the configured directory")
        return

    print(f"Found {len(json_files)} policy file(s)")
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"Pushing policies ({mode}) to the configured endpoint...\n")

    success = 0
    errors = 0
    for filename in json_files:
        filepath = os.path.join(args.policy_dir, filename)
        try:
            with open(filepath) as f:
                policy_data = json.load(f)

            policy = schemas.Policy.model_validate(policy_data)

            if args.dry_run:
                print(f"  [dry-run] {policy.name} — valid, would push")
                success += 1
                continue

            # Idempotent upsert: delete existing, then create
            try:
                client.delete_policy(policy.name)
            except Exception:
                pass  # Policy may not exist yet

            client.create_policy(policy)
            print(f"  [pushed] {policy.name}")
            success += 1

        except Exception as e:
            print(f"  [error]  {filename}: {type(e).__name__}", file=sys.stderr)
            errors += 1

    print(f"\nDone. {success} succeeded, {errors} failed.")
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

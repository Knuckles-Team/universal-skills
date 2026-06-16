#!/usr/bin/env python3
"""Update a non-GitOps Portainer stack's env vars (and optionally its compose
content), then redeploy — the reliable way to inject a new secret/var into a
deployed *-mcp stack.

Why this exists: Portainer "compose"/standalone stacks store BOTH an env list
AND their own copy of the stack file. That stored copy DRIFTS from the repo, so
two failure modes bite:
  1. Adding a value to the env list does nothing if the stored compose has no
     ``- VAR=${VAR}`` line to inject it — the container env stays empty.
  2. Redeploying with the stored (stale) compose silently reverts repo changes
     (e.g. a mount or PYTHONPATH you fixed live).
So this tool merges env overrides AND pushes the *current repo* compose file in
the same update, keeping the deployed stack and the repo in lockstep.

Dependency-free (stdlib urllib). Credentials come from the environment
(PORTAINER_URL, PORTAINER_TOKEN) or --url/--token. No secret is hard-coded.

Usage:
  portainer_stack_env.py --stack-id 262 \
      --set KEYCLOAK_CLIENT_SECRET=... --set KEYCLOAK_REALM=master \
      --compose-file services/keycloak-mcp/compose.yml
  # or read overrides from a JSON file (keeps secrets off argv):
  portainer_stack_env.py --stack-id 262 --set-json /run/overrides.json \
      --compose-file services/keycloak-mcp/compose.yml
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.request

try:
    from agent_utilities.base_utilities import to_boolean
except ImportError:  # keep the skill usable without agent-utilities installed
    def to_boolean(v: object) -> bool:
        return str(v).strip().lower() in ("1", "true", "yes", "on")


def _ctx(verify: bool) -> ssl.SSLContext | None:
    if verify:
        return None
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


def _req(method, url, token, verify, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        url, data=data, method=method,
        headers={"X-API-Key": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(r, timeout=30, context=_ctx(verify)) as resp:
        return json.loads(resp.read() or "{}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stack-id", required=True)
    ap.add_argument("--url", default=os.getenv("PORTAINER_URL", ""))
    ap.add_argument("--token", default=os.getenv("PORTAINER_TOKEN", ""))
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="env override (repeatable)")
    ap.add_argument("--set-json", help="JSON file of {KEY: VALUE} overrides (keeps secrets off argv)")
    ap.add_argument("--compose-file", help="repo stack file to push as the stored compose (recommended)")
    ap.add_argument("--insecure", action="store_true",
                    help="skip TLS verification (default honors PORTAINER_VERIFY)")
    a = ap.parse_args()

    if not a.url or not a.token:
        print("PORTAINER_URL and PORTAINER_TOKEN are required (env or --url/--token)", file=sys.stderr)
        return 2
    verify = not a.insecure and to_boolean(os.getenv("PORTAINER_VERIFY", "True"))
    base = a.url.rstrip("/")

    overrides: dict[str, str] = {}
    if a.set_json:
        overrides.update(json.load(open(a.set_json)))
    for kv in a.set:
        k, _, v = kv.partition("=")
        overrides[k] = v

    stack = _req("GET", f"{base}/api/stacks/{a.stack_id}", a.token, verify)
    eid = stack["EndpointId"]
    env = {e["name"]: e["value"] for e in (stack.get("Env") or [])}
    env.update(overrides)
    if a.compose_file:
        content = open(a.compose_file).read()
    else:
        content = _req("GET", f"{base}/api/stacks/{a.stack_id}/file", a.token, verify)["StackFileContent"]

    _req("PUT", f"{base}/api/stacks/{a.stack_id}?endpointId={eid}", a.token, verify, {
        "env": [{"name": k, "value": v} for k, v in env.items()],
        "stackFileContent": content,
        "prune": False,
        "pullImage": False,
    })
    print("stack %s (%s) redeployed; %d env vars; set/overrode: %s%s" % (
        a.stack_id, stack.get("Name"), len(env), sorted(overrides),
        "; compose replaced from " + a.compose_file if a.compose_file else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

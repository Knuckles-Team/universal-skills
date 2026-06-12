#!/usr/bin/env python3
"""Generate editable streamable-http ``compose.dev.yml`` for the MCP connector fleet.

The central multiplexer proved an "edit locally, run in Docker" loop: instead of a
baked image, run ``python:3.11-slim``, bind-mount the connector's **source**, pip
install it at container start, and run its console script over streamable-http.
Code edits on the host go live on a container restart — no image rebuild, no
registry round-trip.

This generalizes that pattern across the fleet. The **source of truth is
``agent-packages/agents/*``** (the connector packages). The agent directory name
often differs from its deployed stack (``agents/github-agent`` →
``services/github-mcp``, ``agents/clarity-api`` → ``services/clarity-mcp``), so each
agent is mapped to its stack via its ``*-mcp`` console script (from pyproject). For
each connector it writes a ``compose.dev.yml``:

* with a matching ``services/<stack>``: derived from that production ``compose.yml``
  (networks / dns / env / healthcheck / logging preserved);
* without one: from a standard streamable-http template (a new ``services/<mcp>`` dir).

Either way the image becomes ``python:3.11-slim``, the command installs the
bind-mounted **agent source** and execs the MCP console script, and the service is
pinned to the node holding the source.

    gen_editable_compose.py                 # whole fleet
    gen_editable_compose.py --only github-mcp,caddy-mcp --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib

import yaml

EDITABLE_IMAGE = "python:3.11-slim"


def discover(workspace: str) -> list[dict]:
    """Map every connector: agent dir -> mcp console script -> services stack."""
    agents_root = os.path.join(workspace, "agent-packages", "agents")
    services_dir = os.path.join(workspace, "services")
    stacks = {
        e
        for e in os.listdir(services_dir)
        if os.path.isfile(os.path.join(services_dir, e, "compose.yml"))
    }
    out = []
    for agent in sorted(os.listdir(agents_root)):
        adir = os.path.join(agents_root, agent)
        pj = os.path.join(adir, "pyproject.toml")
        if not os.path.isdir(adir) or not os.path.isfile(pj):
            continue
        try:
            scripts = (tomllib.load(open(pj, "rb")).get("project", {}) or {}).get(
                "scripts", {}
            ) or {}
        except Exception:
            scripts = {}
        mcp = [k for k in scripts if k.endswith("-mcp")]
        script = mcp[0] if mcp else (next(iter(scripts)) if scripts else None)
        if not script:
            continue
        candidates = [
            script,
            agent,
            agent.replace("-agent", "-mcp").replace("-api", "-mcp"),
        ]
        stack = next((c for c in candidates if c in stacks), None)
        out.append({"agent": agent, "script": script, "stack": stack})
    return out


def _wrap_command(script: str) -> list[str]:
    return ["sh", "-c", f"pip install --no-cache-dir /src && exec {script}"]


def _template_compose(name: str) -> dict:
    """Standard streamable-http stack for a connector with no production compose."""
    return {
        "version": "3.8",
        "services": {
            name: {
                "hostname": name,
                "restart": "always",
                "networks": ["caddy", "cloudflare", "internet"],
                "dns": ["10.0.0.199"],
                "environment": [
                    "PYTHONUNBUFFERED=1",
                    "HOST=0.0.0.0",
                    "PORT=8000",
                    "TRANSPORT=streamable-http",
                ],
                "healthcheck": {
                    "test": [
                        "CMD",
                        "python3",
                        "-c",
                        "import socket; socket.create_connection(('localhost', 8000), timeout=5)",
                    ],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                "logging": {
                    "driver": "json-file",
                    "options": {"max-size": "10m", "max-file": "3"},
                },
            }
        },
        "networks": {
            "caddy": {"external": True},
            "cloudflare": {"external": True},
            "internet": {"external": True},
        },
    }


def make_editable(
    compose: dict, svc_name: str, source: str, script: str, server: str
) -> dict:
    services = compose.get("services", {})
    if svc_name not in services:
        if len(services) != 1:
            raise ValueError("cannot locate the service entry")
        svc_name = next(iter(services))
    svc = services[svc_name]
    svc["image"] = EDITABLE_IMAGE
    svc["command"] = _wrap_command(script)
    vols = [v for v in svc.get("volumes", []) if ":/src:" not in str(v)]
    vols.insert(0, f"{source}:/src:ro")
    svc["volumes"] = vols
    if isinstance(svc.get("healthcheck"), dict):
        svc["healthcheck"]["start_period"] = "90s"
    deploy = svc.setdefault("deploy", {})
    deploy.setdefault("placement", {})["constraints"] = [
        f"node.labels.name == ${{SERVER:-{server}}}"
    ]
    deploy.setdefault("restart_policy", {"condition": "any"})
    return compose


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--workspace", default=os.environ.get("WORKSPACE", "/home/apps/workspace")
    )
    ap.add_argument("--server", default="RW710")
    ap.add_argument("--only", help="comma-separated stack/script names")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    only = {s.strip() for s in (args.only or "").split(",") if s.strip()}
    connectors = discover(args.workspace)
    derived, templated, skipped = [], [], []

    for c in connectors:
        name = c["stack"] or c["script"]
        if only and name not in only and c["script"] not in only:
            continue
        source = os.path.join(args.workspace, "agent-packages", "agents", c["agent"])
        services_dir = os.path.join(args.workspace, "services")
        if c["stack"]:
            with open(os.path.join(services_dir, c["stack"], "compose.yml")) as f:
                compose = yaml.safe_load(f)
            kind = derived
        else:
            compose = _template_compose(name)
            kind = templated
        try:
            editable = make_editable(compose, name, source, c["script"], args.server)
        except ValueError as e:
            skipped.append(f"{c['agent']} ({e})")
            continue
        out_dir = os.path.join(services_dir, name)
        out = os.path.join(out_dir, "compose.dev.yml")
        header = (
            "# EDITABLE-DEV variant (generated by gen_editable_compose.py).\n"
            "# python:3.11-slim + bind-mounted agent source + runtime pip install;\n"
            f"# source: agent-packages/agents/{c['agent']} (console script: {c['script']}).\n"
            "# Edit the source on the host, restart this service, changes are live.\n"
            f"# Pinned to the node holding the source ({args.server}).\n"
        )
        body = yaml.safe_dump(editable, sort_keys=False, default_flow_style=False)
        if args.dry_run:
            print(f"--- {out} ---\n{header}{body}\n")
        else:
            os.makedirs(out_dir, exist_ok=True)
            with open(out, "w") as f:
                f.write(header + body)
        kind.append(name)

    print(f"derived {len(derived)} (from production compose): {', '.join(derived)}")
    print(f"templated {len(templated)} (no stack — new dir): {', '.join(templated)}")
    if skipped:
        print(f"skipped {len(skipped)}: {', '.join(skipped)}")
    print(f"TOTAL compose.dev.yml: {len(derived) + len(templated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

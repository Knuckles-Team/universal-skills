#!/usr/bin/env python3
"""Inject the agent-os-genesis "Deploy with" block into each agents/* README.

Every connector's README should point operators at the **agent-os-genesis** skill's
single-package deploy mode (install via pip/uvx, editable `-e`, prebuilt image, or the
`compose.dev.yml` editable container — across docker/podman/k8s). This injector renders
the canonical block (see
``universal_skills/workflows/infra/agent-os-genesis/references/package-deploy-readme.md``)
per package and inserts/updates it between idempotent markers, so the rollout across all
~60 packages is generated, not hand-written, and never drifts.

Run::

    python3 scripts/inject_package_deploy_readme.py --agents-dir ../../agents          # write
    python3 scripts/inject_package_deploy_readme.py --agents-dir ../../agents --check   # CI gate
    python3 scripts/inject_package_deploy_readme.py --agents-dir ../../agents --only gitlab-api

Idempotent: re-running replaces the marked block in place; running on a README that
already matches is a no-op. Skips dirs with no README.md or no pyproject.toml.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_DEFAULT_AGENTS = REPO / "../../agents"
BEGIN = "<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->"
END = "<!-- END agent-os-genesis-deploy -->"


def _pkg_meta(agent_dir: Path) -> dict | None:
    """Read package name + console-script base + image from pyproject/mcp_config."""
    pyproject = agent_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', text)
    package = m.group(1) if m else agent_dir.name
    # Console-script base: the `<base>-mcp = ...` entry under [project.scripts].
    sm = re.search(r'(?m)^\s*([a-z0-9][a-z0-9-]*)-mcp\s*=', text)
    name = sm.group(1) if sm else package.replace("-mcp", "").replace("-api", "")
    image = f"knucklessg1/{package}:latest"
    return {"package": package, "name": name, "image": image}


def _block(meta: dict) -> str:
    name, package, image = meta["name"], meta["package"], meta["image"]
    return f"""{BEGIN}

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `{package}` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx {name}-mcp` · or `uv tool install {package}` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `{image}` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

{END}"""


def _apply(readme: Path, block: str) -> bool:
    """Insert or replace the block. Returns True if the file would change."""
    current = readme.read_text(encoding="utf-8") if readme.exists() else ""
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
    if pattern.search(current):
        updated = pattern.sub(block, current)
    else:
        sep = "" if current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
        updated = current + sep + "\n" + block + "\n"
    return updated, updated != current


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agents-dir", type=Path, default=_DEFAULT_AGENTS)
    ap.add_argument("--only", default="", help="restrict to one agent dir name")
    ap.add_argument("--check", action="store_true", help="fail if any README is stale")
    args = ap.parse_args()

    agents = args.agents_dir
    if not agents.exists():
        # As a gate, skip-pass when the agents sibling isn't present (e.g. the
        # universal-skills repo built in isolation); only error in write mode.
        msg = f"inject_package_deploy_readme: agents dir not found: {agents}"
        if args.check:
            print(msg + " — skipped.")
            return 0
        print(msg)
        return 1

    changed: list[str] = []
    skipped: list[str] = []
    for d in sorted(p for p in agents.iterdir() if p.is_dir()):
        if args.only and d.name != args.only:
            continue
        if d.name in {"tests", "__pycache__"}:
            continue
        meta = _pkg_meta(d)
        readme = d / "README.md"
        if meta is None or not readme.exists():
            skipped.append(d.name)
            continue
        updated, will_change = _apply(readme, _block(meta))
        if will_change:
            changed.append(d.name)
            if not args.check:
                readme.write_text(updated, encoding="utf-8")

    if args.check:
        if changed:
            print(f"stale READMEs ({len(changed)}): {', '.join(changed)}")
            return 1
        print(f"all READMEs current ({len(skipped)} skipped).")
        return 0
    print(f"updated {len(changed)} README(s); skipped {len(skipped)} (no README/pyproject).")
    if changed:
        print("  " + ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())

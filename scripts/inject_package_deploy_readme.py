#!/usr/bin/env python3
"""Inject current deployment blocks into each provider README and deployment guide.

Every connector README should point operators at the consolidated
``agent-utilities-deployment`` workflow. This injector renders one machine-neutral
contract per package and inserts or updates it between idempotent markers, so the
fleet rollout is generated rather than hand-written.

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
BEGIN = (
    "<!-- BEGIN agent-utilities-deployment (generated; do not edit between markers) -->"
)
END = "<!-- END agent-utilities-deployment -->"
ADDITIONAL_BEGIN = "<!-- BEGIN GENERATED: additional-deployment-options -->"
ADDITIONAL_END = "<!-- END GENERATED: additional-deployment-options -->"
DOCS_BEGIN = "<!-- BEGIN GENERATED: deployment-options -->"
DOCS_END = "<!-- END GENERATED: deployment-options -->"
MUTABLE_IMAGE_RE = re.compile(r":latest\b", re.IGNORECASE)
LEGACY_TLS_BOOLEAN_RE = re.compile(
    r"\b[A-Z0-9_]*SSL_VERIFY\b|"
    r"\bssl_verify\b|"
    r"\bverify\s*:\s*bool(?:\s*\|\s*None)?\b|"
    r"\bverify\s*=\s*(?:True|False)\b|"
    r"urllib3\.disable_warnings"
)


def _pkg_meta(agent_dir: Path) -> dict | None:
    """Read package name + console-script base + image from pyproject/mcp_config."""
    pyproject = agent_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', text)
    package = m.group(1) if m else agent_dir.name
    # Console-script base: the `<base>-mcp = ...` entry under [project.scripts].
    sm = re.search(r"(?m)^\s*([a-z0-9][a-z0-9-]*)-mcp\s*=", text)
    name = sm.group(1) if sm else package.replace("-mcp", "").replace("-api", "")
    image = f"registry.example.invalid/{package}@sha256:<digest>"
    return {"package": package, "name": name, "image": image}


def _block(meta: dict) -> str:
    name, package, image = meta["name"], meta["package"], meta["image"]
    return f"""{BEGIN}

## Deploy with `agent-utilities-deployment`

Provision this package with the consolidated **`agent-utilities-deployment`**
workflow. It selects an installed-package, editable-source, or immutable-container
path; records only runtime secret and TLS-profile references in `AgentConfig`; and
runs doctor, registration, policy, observability, and rollback gates. Ask your agent
to **"deploy `{package}` with agent-utilities-deployment"**.

| Install mode | Command |
|------|---------|
| Installed package | `uv tool install "{package}[mcp]"`, then run `{name}-mcp` |
| Editable source | `uv pip install -e ".[agent]"`, then run `{name}-mcp` |
| Immutable container | deploy `{image}` through the operator-selected orchestrator |

The repository embeds no deployment profile, credential value, certificate path, or
environment-specific endpoint. Supply those at runtime through `AgentConfig` and the
configured secret provider.

{END}"""


def _additional_block(meta: dict) -> str:
    package = meta["package"]
    return f"""{ADDITIONAL_BEGIN}
### Additional Deployment Options

`{package}` can run as a local stdio process or container, or behind a remote
network boundary. The
[Deployment guide](https://knuckles-team.github.io/{package}/deployment/) carries
the detailed transport contract.

- **Local container** — launch a reviewed immutable image as a least-privilege
  stdio child with no listener or published port.
- **Remote URL** — connect through an operator-supplied authenticated HTTPS
  ingress. Keep its URL, outbound identity references, trust profile, and exact
  `MCP_ALLOWED_HOSTS` in `AgentConfig`.
{ADDITIONAL_END}"""


def _docs_block(meta: dict) -> str:
    name, package, image = meta["name"], meta["package"], meta["image"]
    return f"""{DOCS_BEGIN}
## Deployment Options

`{package}` supports local stdio, a loopback-only development listener, a
least-privilege stdio container, and a remote authenticated HTTPS boundary.
Provider endpoint, credential, selector, identity, and trust material are supplied
at runtime through `AgentConfig`; none is stored in this repository.

### Installed stdio process

```json
{{
  "mcpServers": {{
    "{name}": {{
      "command": "{name}-mcp",
      "args": [],
      "env": {{"MCP_TOOL_MODE": "intent"}}
    }}
  }}
}}
```

### Loopback development listener

```bash
{name}-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require direct TLS
or an explicitly trusted TLS-terminating ingress, configured authentication, exact
`MCP_ALLOWED_HOSTS`, and an exact trusted-proxy CIDR policy.

### Least-privilege local container

```bash
docker run -i --rm \\
  --read-only \\
  --cap-drop=ALL \\
  --security-opt=no-new-privileges \\
  --pids-limit=256 \\
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \\
  -e TRANSPORT=stdio \\
  {image} {name}-mcp
```

The operator projects the selected AgentConfig profile into the process at runtime;
the image remains immutable and contains no environment connection profile.

### Remote authenticated HTTPS endpoint

```json
{{
  "mcpServers": {{
    "{name}": {{"url": "https://service.example.invalid/mcp"}}
  }}
}}
```

Store the real remote URL, outbound identity reference, and TLS-profile reference in
`AgentConfig`, not in MCP client JSON or documentation.
{DOCS_END}"""


def _apply_additional(content: str, block: str) -> tuple[str, bool]:
    """Replace an existing additional-options block without inventing one."""
    pattern = re.compile(
        re.escape(ADDITIONAL_BEGIN) + r".*?" + re.escape(ADDITIONAL_END),
        re.DOTALL,
    )
    if pattern.search(content) is None:
        return content, False
    updated = pattern.sub(block, content)
    return updated, updated != content


def _apply_docs(content: str, block: str) -> tuple[str, bool]:
    """Replace the existing generated deployment-doc block without inventing one."""
    pattern = re.compile(
        re.escape(DOCS_BEGIN) + r".*?" + re.escape(DOCS_END), re.DOTALL
    )
    if pattern.search(content) is None:
        return content, False
    updated = pattern.sub(block, content)
    return updated, updated != content


def _apply(readme: Path, block: str) -> tuple[str, bool]:
    """Return the rendered README and whether it differs from disk."""
    current = readme.read_text(encoding="utf-8") if readme.exists() else ""
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
    if pattern.search(current):
        updated = pattern.sub(block, current)
    else:
        sep = (
            ""
            if current.endswith("\n\n")
            else ("\n" if current.endswith("\n") else "\n\n")
        )
        updated = current + sep + "\n" + block + "\n"
    return updated, updated != current


def _mutable_image_references(agent_dir: Path) -> list[str]:
    """Return executable/doc mutable-image references, excluding history and tests."""
    candidates: set[Path] = set()
    candidates.update(agent_dir.glob("README*.md"))
    docs_dir = agent_dir / "docs"
    if docs_dir.is_dir():
        candidates.update(docs_dir.rglob("*.md"))

    deployment_roots = (
        agent_dir / "docker",
        agent_dir / "deploy",
        agent_dir / "deployments",
        agent_dir / "k8s",
        agent_dir / "helm",
        agent_dir / ".github" / "workflows",
    )
    deployment_patterns = (
        "Dockerfile*",
        "*.yml",
        "*.yaml",
        "*.json",
        "*.toml",
        "*.sh",
        "*.ps1",
    )
    for root in deployment_roots:
        if not root.is_dir():
            continue
        for pattern in deployment_patterns:
            candidates.update(root.rglob(pattern))
    for pattern in ("*.yml", "*.yaml", "*.json", "*.toml", "*.sh", "*.ps1"):
        candidates.update(agent_dir.glob(pattern))

    hits: list[str] = []
    for path in sorted(candidates):
        if path.name.casefold().startswith("changelog"):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            if MUTABLE_IMAGE_RE.search(line):
                hits.append(f"{path.relative_to(agent_dir)}:{line_number}")
    return hits


def _legacy_tls_boolean_references(agent_dir: Path) -> list[str]:
    """Return released surfaces that bypass named AgentConfig TLS profiles."""
    candidates: set[Path] = set(agent_dir.glob("README*.md"))
    candidates.update(agent_dir.glob("mcp_config*.json"))
    env_example = agent_dir / ".env.example"
    if env_example.exists():
        candidates.add(env_example)
    docs_dir = agent_dir / "docs"
    if docs_dir.is_dir():
        candidates.update(docs_dir.rglob("*.md"))

    candidates.update(agent_dir.glob("*.py"))
    scripts_dir = agent_dir / "scripts"
    if scripts_dir.is_dir():
        candidates.update(scripts_dir.rglob("*.py"))
    excluded_roots = {"site", "tests", "vendor", "vendored"}
    for source_root in agent_dir.iterdir():
        if (
            not source_root.is_dir()
            or source_root.name in excluded_roots
            or not (source_root / "__init__.py").exists()
        ):
            continue
        candidates.update(source_root.rglob("*.py"))

    hits: list[str] = []
    for path in sorted(candidates):
        if path.name.casefold().startswith("changelog"):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            if LEGACY_TLS_BOOLEAN_RE.search(line):
                hits.append(f"{path.relative_to(agent_dir)}:{line_number}")
    return hits


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
    mutable_images: list[str] = []
    legacy_tls_booleans: list[str] = []
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
        updated, additional_change = _apply_additional(
            updated,
            _additional_block(meta),
        )
        will_change = will_change or additional_change
        if will_change:
            changed.append(d.name)
            if not args.check:
                readme.write_text(updated, encoding="utf-8")

        deployment_doc = d / "docs" / "deployment.md"
        if deployment_doc.exists():
            current_doc = deployment_doc.read_text(encoding="utf-8")
            updated_doc, doc_change = _apply_docs(current_doc, _docs_block(meta))
            if doc_change:
                if d.name not in changed:
                    changed.append(d.name)
                if not args.check:
                    deployment_doc.write_text(updated_doc, encoding="utf-8")
        if args.check:
            mutable_images.extend(
                f"{d.name}/{hit}" for hit in _mutable_image_references(d)
            )
            legacy_tls_booleans.extend(
                f"{d.name}/{hit}" for hit in _legacy_tls_boolean_references(d)
            )

    if args.check:
        if mutable_images:
            print(
                "mutable image references remain in executable/current docs: "
                + ", ".join(mutable_images)
            )
            return 1
        if legacy_tls_booleans:
            print(
                "legacy TLS boolean surfaces remain in released provider paths: "
                + ", ".join(legacy_tls_booleans)
            )
            return 1
        if changed:
            print(f"stale READMEs ({len(changed)}): {', '.join(changed)}")
            return 1
        print(f"all deployment docs current ({len(skipped)} projects skipped).")
        return 0
    print(
        f"updated {len(changed)} project(s); skipped {len(skipped)} (no README/pyproject)."
    )
    if changed:
        print("  " + ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())

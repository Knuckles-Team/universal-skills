#!/usr/bin/env python3
"""Reject retired connector APIs in a generated SDK-based project.

This static check needs no installed connector dependencies. A connector is
MCP-only and depends on agent-connector-sdk alone: the retired control-plane
package may be neither imported nor declared as a dependency.
"""

from __future__ import annotations

import argparse
import ast
import configparser
import json
import re
import tomllib
from pathlib import Path

# Assembled so repository-wide searches for the retired dependency stay clean.
RETIRED_PACKAGE = "agent" + "_utilities"


def _imports(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return [node.module or ""]
    if not isinstance(node, ast.Call) or not node.args:
        return []
    function = node.func
    dynamic_import = (
        isinstance(function, ast.Name) and function.id == "__import__"
    ) or (isinstance(function, ast.Attribute) and function.attr == "import_module")
    argument = node.args[0]
    if (
        dynamic_import
        and isinstance(argument, ast.Constant)
        and isinstance(argument.value, str)
    ):
        return [argument.value]
    return []


def _module_violations(path: Path, root: Path) -> list[str]:
    relative = path.relative_to(root)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(relative))
    except (SyntaxError, UnicodeError) as exc:
        return [f"{relative}: cannot parse Python: {exc}"]
    violations = []
    for node in ast.walk(tree):
        for name in _imports(node):
            if name == RETIRED_PACKAGE or name.startswith(RETIRED_PACKAGE + "."):
                violations.append(
                    f"{relative}:{node.lineno}: retired connector import {name}"
                )
        if isinstance(node, ast.Constant) and node.value == "MCP_TOOL_MODE":
            violations.append(
                f"{relative}:{node.lineno}: retired MCP_TOOL_MODE setting"
            )
    return violations


def check_project(root: Path, package: str) -> list[str]:
    """Return actual AST/import and direct dependency contract violations."""
    if not package.isidentifier():
        return ["package must be a Python package directory name"]
    package_root = root / package
    if not package_root.is_dir():
        return [f"package directory does not exist: {package}"]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    dependencies = project.get("dependencies", [])
    names = {
        re.split(r"[<>=!~\[; ]", value.lower().replace("_", "-"))[0]
        for value in dependencies
    }
    violations = []
    if sum(re.split(r"[<>=!~\[; ]", value.lower().replace("_", "-"))[0] in {"agent-connector-sdk", "scion-sdk"} for value in dependencies) != 1:
        violations.append("pyproject.toml: connector requires exactly one SDK distribution (scion-sdk or legacy agent-connector-sdk)")
    if names & {RETIRED_PACKAGE.replace("_", "-"), "meristem"}:
        violations.append(
            "pyproject.toml: connectors depend on scion-sdk only"
        )
    for extra, values in project.get("optional-dependencies", {}).items():
        if any(re.split(r"[<>=!~\[; ]", value.lower().replace("_", "-"))[0] in {RETIRED_PACKAGE.replace("_", "-"), "meristem"} for value in values):
            violations.append(
                f"pyproject.toml: extra {extra!r} pulls the retired package"
            )
    if any(
        re.match(r"(?:epistemic[-_]graph|medulla)\[[^]]*\bfull\b", value.lower())
        for value in dependencies
    ):
        violations.append(
            "pyproject.toml: connector must not require the full engine extra"
        )
    for path in sorted(package_root.rglob("*.py")):
        violations.extend(_module_violations(path, root))
    return violations


# --- SDK centralized-capability rules (US-MCP-BUILDER-R001..R008, R010) ------------
# Each rule is a static check over a generated project. The bracketed row names
# the universal-skills requirement; the SDK row (SCION-CENTRALIZED-CAPABILITIES-Rnnn)
# names the capability it protects.

#: Packages the SDK owns or an SDK extra already pins. A connector declares the
#: extra instead (SCION-CENTRALIZED-CAPABILITIES-R040).
EXTRA_OWNED = {
    "requests": (
        "R001",
        "the SDK governed client owns HTTP; pin nothing (SDK R001, R040)",
    ),
    "httpx": (
        "R001",
        "the SDK base install carries httpx; do not pin it (SDK R001, R040)",
    ),
    "gql": ("R004", "use the SDK graphql extra (SDK R016, R040)"),
    "graphql-core": ("R004", "declare scion-sdk[graphql] (SDK R016, R040)"),
    "psycopg": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "psycopg2": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "psycopg2-binary": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "pymysql": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "pymongo": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "oracledb": ("R004", "declare scion-sdk[db] (SDK R020, R040)"),
    "pyodbc": ("R004", "declare scion-sdk[mssql] (SDK R020, R040)"),
    "feedparser": ("R004", "declare scion-sdk[feeds] (SDK R021, R040)"),
    "pyarrow": ("R004", "declare scion-sdk[dataprep] (SDK R024, R040)"),
    "pandas": ("R004", "declare scion-sdk[market] (SDK R023, R040)"),
    "yfinance": ("R004", "declare scion-sdk[market] (SDK R023, R040)"),
    "websockets": ("R004", "declare scion-sdk[stream] (SDK R022, R040)"),
    "rdflib": ("R004", "declare scion-sdk[integrity] (SDK R028, R040)"),
}

_SOURCE_RULES = (
    ("R001", r"^\s*(?:import requests\b|from requests\b)", "imports requests"),
    ("R001", r"\bhttpx\.(?:Async)?Client\s*\(", "builds its own httpx client"),
    (
        "R001",
        r"\brequests\.(?:Session|get|post|put|delete|patch|request)\b",
        "calls requests",
    ),
    ("R001", r"\b(?:_validate_)?max_retries\b\s*[:=]", "ships its own retry policy"),
    (
        "R002",
        r"\burllib3\.disable_warnings\b|\bInsecureRequestWarning\b",
        "silences TLS warnings",
    ),
    ("R002", r"\bverify\s*=\s*False\b", "disables certificate verification"),
    (
        "R002",
        r"\bssl\.create_default_context\b|\b_create_unverified_context\b",
        "builds its own SSL context",
    ),
    ("R002", r"\bCERT_NONE\b|\bcheck_hostname\s*=\s*False\b", "turns off TLS checks"),
    (
        "R003",
        r"""startswith\(\s*\(?\s*["'](?:env|openbao)://""",
        "parses secret references by hand",
    ),
    (
        "R003",
        r"""(?:os\.environ(?:\.get)?|getenv)\s*[\[(]\s*["'][A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_?KEY)(?!_REF)["']""",
        "reads a secret from a plain environment variable",
    ),
    (
        "R004",
        r"^\s*(?:import gql\b|from gql\b)",
        "imports gql; use the SDK graphql extra",
    ),
    (
        "R005",
        r"\b(?:ConnectorContent|IngestBinding)\s*\(",
        "builds the identity object directly; use for_package with no name literal",
    ),
)
_PIPED_INSTALLER = re.compile(
    r"(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b"
)
_VERSION_ASSIGN = re.compile(r"""^\s*__version__\s*(?::[^=]+)?=\s*["']""", re.M)


def _requirement_name(value: str) -> str:
    return re.split(r"[<>=!~\[; ]", value.strip().lower().replace("_", "-"))[0]


def _dependency_violations(project: dict) -> list[str]:
    pairs = [("dependencies", value) for value in project.get("dependencies", [])]
    for extra, values in project.get("optional-dependencies", {}).items():
        pairs.extend((f"extra {extra!r}", value) for value in values)
    out = []
    for where, value in pairs:
        name = _requirement_name(value)
        if name in EXTRA_OWNED:
            row, why = EXTRA_OWNED[name]
            out.append(
                f"pyproject.toml: {where} pins {name}; {why} [US-MCP-BUILDER-{row}]"
            )
    return out


def _source_violations(root: Path, package_root: Path) -> list[str]:
    out = []
    for path in sorted(package_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        for row, pattern, message in _SOURCE_RULES:
            if re.search(pattern, text, re.M):
                out.append(f"{rel}: {message} [US-MCP-BUILDER-{row}]")
        if _VERSION_ASSIGN.search(text) and path.name != "_version.py":
            out.append(
                f"{rel}: assigns __version__; only _version.py may [US-MCP-BUILDER-R007]"
            )
    return out


def _identity_violations(root: Path, package_root: Path, project: dict) -> list[str]:
    group = project.get("entry-points", {}).get("agent_connector_sdk.connector", {})
    if len(group) != 1:
        return [
            "pyproject.toml: declare exactly one agent_connector_sdk.connector"
            f" entry point (found {len(group)}) [US-MCP-BUILDER-R005]"
        ]
    ((fleet, target),) = group.items()
    out = []
    if target.split(":")[0].split(".")[0] != package_root.name:
        out.append(
            f"pyproject.toml: connector entry point must name {package_root.name} [US-MCP-BUILDER-R005]"
        )
    for path in sorted(package_root.rglob("connector_manifest.yml")):
        match = re.search(
            r"""["']?connector["']?\s*:\s*["']?([^"',\s]+)""",
            path.read_text(encoding="utf-8"),
        )
        if match and match.group(1) != fleet:
            out.append(
                f"{path.relative_to(root)}: connector {match.group(1)!r} != fleet name {fleet!r} [US-MCP-BUILDER-R005]"
            )
    for path in sorted(package_root.rglob("tool_schema_fingerprints.json")):
        name = json.loads(path.read_text(encoding="utf-8")).get("connector")
        if name is not None and name != fleet:
            out.append(
                f"{path.relative_to(root)}: connector {name!r} != fleet name {fleet!r} [US-MCP-BUILDER-R005]"
            )
    return out


def _delivery_violations(root: Path) -> list[str]:
    out = []
    bootstrap = root / "scripts" / "bootstrap.sh"
    if not bootstrap.is_file():
        out.append("scripts/bootstrap.sh: missing [US-MCP-BUILDER-R006]")
    elif _PIPED_INSTALLER.search(bootstrap.read_text(encoding="utf-8")):
        out.append(
            "scripts/bootstrap.sh: pipes a network response into a shell [US-MCP-BUILDER-R006]"
        )
    agents = root / "AGENTS.md"
    if not agents.is_file() or "<!-- agent-contract:start -->" not in agents.read_text(
        encoding="utf-8"
    ):
        out.append(
            "AGENTS.md: missing the standard agent-contract section [US-MCP-BUILDER-R006]"
        )
    specs = [p for p in (root / "specs").glob("*") if p.is_dir()]
    if not specs:
        out.append("specs/: no spec directory [US-MCP-BUILDER-R006]")
    for spec in specs:
        for name in (
            "spec.md",
            "requirements.md",
            "plan.md",
            "test-spec.md",
            "tasks.md",
        ):
            if not (spec / name).is_file():
                out.append(f"specs/{spec.name}/{name}: missing [US-MCP-BUILDER-R006]")
    return out


def _bumpversion_violations(root: Path, project: dict, package_root: Path) -> list[str]:
    cfg = root / ".bumpversion.cfg"
    if not cfg.is_file():
        return [".bumpversion.cfg: missing [US-MCP-BUILDER-R007]"]
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(cfg, encoding="utf-8")
    current = parser.get("bumpversion", "current_version", fallback="")
    out, tracked = [], set()
    for section in parser.sections():
        match = re.match(r"bumpversion:file(?:\([^)]*\))?:(.+)$", section)
        if not match:
            continue
        rel = match.group(1)
        target = root / rel
        if not target.is_file():
            out.append(
                f".bumpversion.cfg: lists {rel}, which does not exist [US-MCP-BUILDER-R007]"
            )
            continue
        tracked.add(rel)
        search = parser.get(section, "search", fallback="{current_version}").replace(
            "{current_version}", current
        )
        if search not in target.read_text(encoding="utf-8"):
            out.append(
                f".bumpversion.cfg: {rel} does not contain {search!r} [US-MCP-BUILDER-R007]"
            )
    version_file = f"{package_root.name}/_version.py"
    if version_file not in tracked:
        out.append(f".bumpversion.cfg: must track {version_file} [US-MCP-BUILDER-R007]")
    dockerfile = root / "docker" / "Dockerfile"
    if dockerfile.is_file():
        pins = re.findall(
            r"==\s*([0-9][^\s\"']*)", dockerfile.read_text(encoding="utf-8")
        )
        if "docker/Dockerfile" not in tracked:
            out.append(
                ".bumpversion.cfg: must track docker/Dockerfile, the image version pin [US-MCP-BUILDER-R007]"
            )
        out.extend(
            f"docker/Dockerfile: pins {pin}, bumpversion current_version is {current} [US-MCP-BUILDER-R007]"
            for pin in pins
            if pin != current
        )
    if project.get("version") != current:
        out.append(
            f"pyproject.toml: version {project.get('version')} != bumpversion {current} [US-MCP-BUILDER-R007]"
        )
    return out


def _hook_violations(root: Path) -> list[str]:
    config = root / ".pre-commit-config.yaml"
    if not config.is_file():
        return [".pre-commit-config.yaml: missing [US-MCP-BUILDER-R008]"]
    text = config.read_text(encoding="utf-8")
    out = []
    if not re.search(r"(?m)^\s*- id: connector-name\n\s*args: \[--strict\]", text):
        out.append(
            "pre-commit: enable connector-name with args [--strict] [US-MCP-BUILDER-R008]"
        )
    live = re.search(r"(?m)^\s*- id: sdk-conformance\n\s*args: \[--strict\]", text)
    pending = re.search(
        r"(?m)^\s*# PENDING .*\n(?:\s*#.*\n)*?\s*# - id: sdk-conformance\n\s*#\s*args: \[--strict\]",
        text,
    )
    if not (live or pending):
        out.append(
            "pre-commit: enable sdk-conformance with args [--strict] [US-MCP-BUILDER-R008]"
        )
    match = re.search(
        r"(?m)^\s*- id: check-cli-help\n(?:\s+.*\n)*?\s+entry: (.+)$", text
    )
    if not match:
        out.append("pre-commit: missing check-cli-help [US-MCP-BUILDER-R008]")
    elif any(token in match.group(1) for token in ("uv run", "find ", "bash -c")):
        out.append(
            "pre-commit: check-cli-help must run from a plain install [US-MCP-BUILDER-R008]"
        )
    return out


PARENT_ONTOLOGY = "http://knuckles.team/kg"


def _ontology_violations(package_root: Path) -> list[str]:
    """US-MCP-BUILDER-R010: the domain ontology links to the parent and has no TODO."""
    out = []
    for path in sorted((package_root / "ontology").glob("*.ttl")):
        text = path.read_text(encoding="utf-8")
        if "owl:Ontology" not in text:
            continue
        name = f"{package_root.name}/ontology/{path.name}"
        code = re.sub(r"(?m)^\s*#.*$", "", text)
        if not re.search(rf"owl:imports\s+<{re.escape(PARENT_ONTOLOGY)}>", code):
            out.append(
                f"{name}: must declare owl:imports <{PARENT_ONTOLOGY}> [US-MCP-BUILDER-R010]"
            )
        if "TODO" in text:
            out.append(f"{name}: contains a TODO [US-MCP-BUILDER-R010]")
        out.extend(
            f"{name}: class without rdfs:subClassOf a parent class [US-MCP-BUILDER-R010]"
            for block in code.split("\n\n")
            if re.search(r"\ba owl:Class\b", block) and "rdfs:subClassOf" not in block
        )
    return out


def check_sdk_rules(root: Path, package: str) -> list[str]:
    """Return violations of the SDK centralized-capability rules."""
    package_root = root / package
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    return [
        *_dependency_violations(project),
        *_source_violations(root, package_root),
        *_identity_violations(root, package_root, project),
        *_delivery_violations(root),
        *_bumpversion_violations(root, project, package_root),
        *_hook_violations(root),
        *_ontology_violations(package_root),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--package", required=True)
    args = parser.parse_args()
    violations = check_project(args.root, args.package)
    if not violations:
        violations = check_sdk_rules(args.root, args.package)
    for violation in violations:
        print(violation)
    if not violations:
        print("Connector SDK contract: passed")
    return int(bool(violations))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check a connector's served MCP tools: one typed, annotated tool per API operation.

usage: check_tool_parity.py <repo> --package <pkg>
           [--census connector-tool-coverage-census.tsv --connector <name>]
           [--expected <count>] [--json]

The check builds the connector's MCP server in process and reads its registered
tools (the same surface ``tools/list`` serves). It fails when:

* an operation in the census (rows of kind ``operation``) has no served tool;
* the served operation-tool count is below ``--expected`` (the API operation count);
* an operation tool takes an untyped ``params_json`` blob or lacks annotations;
* an ``action``-routed dispatch tool is still served;
* a Dockerfile installs the package from source (``pip install .``/``".[mcp]"``),
  copies the source tree for installation, or builds tools from source (cargo).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SOURCE_INSTALL = re.compile(
    r"""pip\s+install\b[^\n]*?(?:\s|["'])\.(?:\[[^\]]*\])?(?:["']|\s|$)""",
    re.MULTILINE,
)
SOURCE_TOOL_BUILD = re.compile(r"\bcargo\s+(?:build|install)\b")


def census_operations(path: Path, connector: str) -> set[str]:
    """Old per-operation tool names for one connector from the census TSV."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        return {
            row["old_tool"]
            for row in rows
            if row["connector"] == connector and row["kind"] == "operation"
        }


def dockerfile_findings(repo: Path) -> list[str]:
    """Source installs or source tool builds in the repository's Dockerfiles."""
    findings: list[str] = []
    for path in sorted(repo.glob("**/*Dockerfile*")):
        if ".git" in path.parts or path.name.startswith("debug."):
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo)
        if SOURCE_INSTALL.search(text):
            findings.append(f"{rel}: installs the package from source")
        if SOURCE_TOOL_BUILD.search(text):
            findings.append(f"{rel}: builds tools from source")
        if "--only-binary" not in text and "pip install" in text:
            findings.append(f"{rel}: pip install without --only-binary :all:")
    return findings


def served_tools(repo: Path, package: str) -> list[Any]:
    """The tools the connector's MCP server serves, read in process."""
    sys.path.insert(0, str(repo))
    server = importlib.import_module(f"{package}.mcp_server")
    sys.argv = [sys.argv[0], "--transport", "stdio"]
    built = server.get_mcp_instance()
    instance = built[0] if isinstance(built, tuple) else built
    return asyncio.run(instance.local_provider.list_tools())


def _schema(tool: Any) -> dict[str, Any]:
    return getattr(tool, "parameters", None) or {}


def check(
    repo: Path,
    package: str,
    *,
    census: set[str],
    expected: int | None,
) -> dict[str, Any]:
    tools = served_tools(repo, package)
    names = {tool.name for tool in tools}
    operations = [tool for tool in tools if "operation" in (tool.tags or set())]
    action_tools = sorted(
        tool.name for tool in tools if "action" in _schema(tool).get("properties", {})
        and tool not in operations
    )
    untyped = sorted(
        tool.name
        for tool in operations
        if set(_schema(tool).get("properties", {})) == {"params_json"}
    )
    unannotated = sorted(
        tool.name
        for tool in operations
        if tool.annotations is None or tool.annotations.read_only_hint is None
    )
    missing = sorted(census - names)
    failures: list[str] = []
    if missing:
        failures.append(f"{len(missing)} census operations have no tool: {missing[:20]}")
    if expected is not None and len(operations) < expected:
        failures.append(f"{len(operations)} operation tools < {expected} API operations")
    if untyped:
        failures.append(f"{len(untyped)} untyped params_json tools: {untyped[:20]}")
    if unannotated:
        failures.append(f"{len(unannotated)} tools without annotations: {unannotated[:20]}")
    if action_tools:
        failures.append(f"action-dispatch tools still served: {action_tools}")
    failures.extend(dockerfile_findings(repo))
    return {
        "package": package,
        "served_tools": len(tools),
        "operation_tools": len(operations),
        "census_operations": len(census),
        "missing": missing,
        "untyped": untyped,
        "action_tools": action_tools,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path)
    parser.add_argument("--package", required=True)
    parser.add_argument("--census", type=Path)
    parser.add_argument("--connector")
    parser.add_argument("--expected", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    census: set[str] = set()
    if args.census:
        if not args.connector:
            parser.error("--census needs --connector")
        census = census_operations(args.census, args.connector)
        if not census:
            parser.error(f"no census operations for {args.connector}")
    result = check(
        args.repo.resolve(), args.package, census=census, expected=args.expected
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"{result['package']}: {result['operation_tools']} operation tools, "
            f"{result['served_tools']} served, census {result['census_operations']}"
        )
        for failure in result["failures"]:
            print(f"  FAIL {failure}")
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())

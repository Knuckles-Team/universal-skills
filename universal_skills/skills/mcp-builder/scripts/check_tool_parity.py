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
import tomllib
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


NO_BINARY = re.compile(r"--no-binary[=\s]+([^\s\\]+)")


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def declared_source_builds(repo: Path) -> set[str]:
    """``[tool.pipelines] allow-source-build`` from the repo's pyproject."""
    path = repo / "pyproject.toml"
    if not path.is_file():
        return set()
    section = tomllib.loads(path.read_text(encoding="utf-8")).get("tool", {}).get("pipelines", {})
    return {_normalize(name) for name in section.get("allow-source-build", [])}


def dockerfile_findings(repo: Path) -> list[str]:
    """Source installs or source tool builds in the repository's Dockerfiles.

    ``--no-binary`` is accepted only for exact names the repo declares in
    ``[tool.pipelines] allow-source-build``; never for ``:all:``.
    """
    findings: list[str] = []
    allowed = declared_source_builds(repo)
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
        for raw in NO_BINARY.findall(text):
            for name in raw.split(","):
                if _normalize(name) not in allowed:
                    findings.append(
                        f"{rel}: --no-binary {name} is not in [tool.pipelines] allow-source-build"
                    )
    return findings


def served_tools(repo: Path, package: str) -> tuple[list[Any], list[dict[str, str]]]:
    """The tools the connector's MCP server serves, and its split report, read in process.

    The report (``scion_sdk.mcp.action_split.action_split_report``,
    SDK >= 0.3.5) names the tool that serves each action of a split
    action-routed tool; it is empty on older SDKs.
    """
    sys.path.insert(0, str(repo))
    server = importlib.import_module(f"{package}.mcp_server")
    sys.argv = [sys.argv[0], "--transport", "stdio"]
    built = server.get_mcp_instance()
    instance = built[0] if isinstance(built, tuple) else built
    tools = asyncio.run(instance.local_provider.list_tools())
    try:
        from scion_sdk.mcp.action_split import action_split_report
    except ImportError:
        return tools, []
    return tools, action_split_report(instance)


def _schema(tool: Any) -> dict[str, Any]:
    return getattr(tool, "parameters", None) or {}


def declared_retired_tools(repo: Path) -> set[str]:
    """``[tool.pipelines] retired-tools`` from the repo's pyproject."""
    path = repo / "pyproject.toml"
    if not path.is_file():
        return set()
    section = tomllib.loads(path.read_text(encoding="utf-8")).get("tool", {}).get("pipelines", {})
    return {str(name) for name in section.get("retired-tools", [])}


def covered_tools(report: list[dict[str, str]], served: set[str]) -> set[str]:
    """Names whose actions a served per-operation tool covers, from the split report.

    Both the action-routed tool and each ``<tool>_<action>`` name the SDK did
    not register count, as long as the tool named as serving them is served.
    """
    covered: set[str] = set()
    for entry in report:
        if entry.get("served_by") in served:
            covered.update({entry.get("split", ""), entry.get("tool", "")})
    return covered - {""}


def lost_tools(
    previous: set[str],
    served: set[str],
    retired: set[str],
    covered: set[str] | None = None,
) -> list[str]:
    """Previous-release tools with no successor and no explicit retirement.

    A successor is the same name, a split ``<name>_<action>`` tool, or a
    per-operation tool that covers it (``covered``, from the SDK split report).
    """
    return sorted(
        name
        for name in previous
        if name not in served
        and name not in retired
        and name not in (covered or set())
        and not any(other.startswith(name + "_") for other in served)
    )


def check(
    repo: Path,
    package: str,
    *,
    census: set[str],
    expected: int | None,
    previous: set[str] | None = None,
) -> dict[str, Any]:
    tools, report = served_tools(repo, package)
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
    covered = covered_tools(report, names)
    lost = lost_tools(previous or set(), names, declared_retired_tools(repo), covered)
    if lost:
        failures.append(
            f"{len(lost)} tools of the previous release have no successor "
            f"(list them in [tool.pipelines] retired-tools to retire): {lost[:20]}"
        )
    return {
        "package": package,
        "served_tools": len(tools),
        "operation_tools": len(operations),
        "census_operations": len(census),
        "missing": missing,
        "untyped": untyped,
        "action_tools": action_tools,
        "lost": lost,
        "covered_by_operation": sorted(covered & (previous or set())),
        "names": sorted(names),
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
    parser.add_argument(
        "--previous",
        type=Path,
        help="file of tool names served by the previous release (one per line); "
        "every one needs a successor or a [tool.pipelines] retired-tools entry",
    )
    parser.add_argument(
        "--dump-names", type=Path, help="write the served tool names to this file"
    )
    args = parser.parse_args()
    census: set[str] = set()
    if args.census:
        if not args.connector:
            parser.error("--census needs --connector")
        census = census_operations(args.census, args.connector)
        if not census:
            parser.error(f"no census operations for {args.connector}")
    previous = (
        {line.strip() for line in args.previous.read_text().splitlines() if line.strip()}
        if args.previous
        else None
    )
    result = check(
        args.repo.resolve(),
        args.package,
        census=census,
        expected=args.expected,
        previous=previous,
    )
    if args.dump_names:
        args.dump_names.write_text("\n".join(result["names"]) + "\n")
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

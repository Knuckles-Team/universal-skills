"""Built connector artifacts retain executable contracts and optional entry points.

MCP_BUILDER_BUILD_PYTHON may select an existing build environment when the SDK
test environment does not contain build/setuptools. No dependency installation
or native compilation is performed.
"""

from __future__ import annotations

import ast
import configparser
import json
import os
import subprocess
import sys
import tarfile
import textwrap
import zipfile
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
PACKAGE = "distribution_demo"
DISTRIBUTION = "distribution-demo"
COMBINATIONS = (
    "api_client,mcp",
    "cli,mcp",
    "api_client,mcp,graphql",
)


def _run(arguments, root, env, *, python=None):
    result = subprocess.run(
        [python or sys.executable, *arguments],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture(scope="module", params=COMBINATIONS)
def artifacts(request, tmp_path_factory):
    scratch = tmp_path_factory.mktemp("builder-distribution")
    env = dict(os.environ)
    env.update(
        MCP_FLEET_REGISTRATION="false",
        AUTH_TYPE="none",
        HOST="127.0.0.1",
        TRANSPORT="stdio",
        SYSTEMTOOL="true",
        MCP_ENABLED_TOOLS="",
        MCP_DISABLED_TOOLS="",
        XDG_CONFIG_HOME=str(scratch / "config"),
        PYTHONDONTWRITEBYTECODE="1",
    )
    build_python = env.get("MCP_BUILDER_BUILD_PYTHON", sys.executable)
    _run(
        [
            str(SCRIPTS / "scaffold_package.py"),
            DISTRIBUTION,
            "--output-dir",
            str(scratch),
            "--type",
            request.param,
        ],
        scratch,
        env,
        python=build_python,
    )
    source = scratch / DISTRIBUTION
    _run(
        ["-m", "build", "--sdist", "--wheel", "--no-isolation"],
        source,
        env,
        python=build_python,
    )
    extracted = scratch / "source-artifact"
    extracted.mkdir()
    with tarfile.open(next((source / "dist").glob("*.tar.gz"))) as archive:
        archive.extractall(extracted, filter="data")
    sdist = next(extracted.iterdir())
    wheel = scratch / "wheel-artifact"
    with zipfile.ZipFile(next((source / "dist").glob("*.whl"))) as archive:
        archive.extractall(wheel)
    return source, sdist, wheel, request.param.split(","), env


def test_sdist_preserves_and_executes_generated_contract_scripts(artifacts):
    source, sdist, _, _, env = artifacts
    expected = {
        path.relative_to(source)
        for path in (source / "scripts").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert {
        Path("scripts/check_connector_contract.py"),
        Path("scripts/generate_tool_schemas.py"),
    } <= expected
    for relative in expected:
        assert (sdist / relative).read_bytes() == (source / relative).read_bytes()
    for directory in ("specs", ".pipeline-theme"):
        for path in (source / directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                relative = path.relative_to(source)
                assert (sdist / relative).read_bytes() == path.read_bytes()
    result = _run(
        ["scripts/check_connector_contract.py", ".", "--package", PACKAGE],
        sdist,
        env,
    )
    assert "Connector SDK contract: passed" in result.stdout
    stale = sdist / PACKAGE / "stale.py"
    stale.write_text(
        "from agent_utilities.mcp.server_factory import create_mcp_server\n"
    )
    rejected = subprocess.run(
        [
            sys.executable,
            "scripts/check_connector_contract.py",
            ".",
            "--package",
            PACKAGE,
        ],
        cwd=sdist,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    stale.unlink()
    assert rejected.returncode == 1
    assert (
        "stale.py" in rejected.stdout and "retired connector import" in rejected.stdout
    )


def test_wheel_entry_points_resolve_to_packaged_definitions(artifacts):
    source, _, wheel, _, _ = artifacts
    metadata = next(wheel.glob("*.dist-info/entry_points.txt"))
    entries = configparser.ConfigParser()
    entries.read(metadata)
    assert set(entries["console_scripts"]) == {DISTRIBUTION + "-mcp"}
    for target in entries["console_scripts"].values():
        module, name = target.split(":")
        source_path = wheel.joinpath(*module.split(".")).with_suffix(".py")
        tree = ast.parse(source_path.read_text())
        assert any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
            for node in tree.body
        ), target
    package = source / PACKAGE
    for path in package.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(source)
            assert (wheel / relative).read_bytes() == path.read_bytes(), relative
    main = ast.parse((wheel / PACKAGE / "__main__.py").read_text())
    assert any(isinstance(node, ast.ImportFrom) for node in main.body)


IMPORT_ENTRY_POINTS = textwrap.dedent("""
    import importlib.abc
    import importlib.metadata
    from pathlib import Path
    import socket
    import sys

    class NoOptionalRuntime(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname == "agent_utilities" or fullname.startswith("agent_utilities."):
                raise ModuleNotFoundError("optional agent runtime unavailable")
            return None

    def no_network(*args, **kwargs):
        raise AssertionError("artifact import attempted network access")

    socket.socket.connect = no_network
    sys.meta_path.insert(0, NoOptionalRuntime())
    root = Path(sys.argv[1])
    sys.path.insert(0, str(root))
    distribution = next(importlib.metadata.distributions(path=[str(root)]))
    for entry in distribution.entry_points:
        if entry.group == "console_scripts":
            assert callable(entry.load()), entry.name
    assert not any(name.startswith("agent_utilities") for name in sys.modules)
""")


def test_wheel_entry_points_import_without_optional_agent_runtime(artifacts):
    pytest.importorskip("agent_connector_sdk.mcp.server")
    _, _, wheel, _, env = artifacts
    _run(["-c", IMPORT_ENTRY_POINTS, str(wheel)], wheel.parent, env)


SCHEMA_COMMAND = textwrap.dedent("""
    import runpy
    import socket
    import sys

    def no_network(*args, **kwargs):
        raise AssertionError("schema generation attempted network access")

    socket.socket.connect = no_network
    sys.argv = ["scripts/generate_tool_schemas.py", *sys.argv[1:]]
    runpy.run_path(sys.argv[0], run_name="__main__")
""")


def test_sdist_schema_cli_generates_and_checks_live_contracts(artifacts):
    pytest.importorskip("agent_connector_sdk.mcp.server")
    _, sdist, _, _, env = artifacts
    help_result = _run(["-c", SCHEMA_COMMAND, "--help"], sdist, env)
    assert "--check" in help_result.stdout
    _run(["-c", SCHEMA_COMMAND], sdist, env)
    _run(["-c", SCHEMA_COMMAND, "--check"], sdist, env)
    contracts = json.loads((sdist / "schemas/mcp_tools.json").read_text())
    assert contracts["tools"]
    assert all(
        tool["inputSchema"] and tool["outputSchema"] and tool["compatibility_sha256"]
        for tool in contracts["tools"].values()
    )

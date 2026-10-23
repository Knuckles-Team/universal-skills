"""Generate a real connector and verify its static and offline MCP contracts."""

from __future__ import annotations

import fnmatch
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import tomllib

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)


def _run(
    arguments: list[str], root: Path, env: dict[str, str]
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture
def generated(tmp_path):
    env = dict(os.environ)
    env.update(
        {
            "MCP_FLEET_REGISTRATION": "false",
            "AUTH_TYPE": "none",
            "HOST": "127.0.0.1",
            "TRANSPORT": "stdio",
            "SYSTEMTOOL": "true",
            "MCP_ENABLED_TOOLS": "",
            "MCP_DISABLED_TOOLS": "",
            "XDG_CONFIG_HOME": str(tmp_path / "config"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    _run(
        [
            str(SCRIPTS / "scaffold_package.py"),
            "contract-smoke",
            "--output-dir",
            str(tmp_path),
            "--type",
            "api_client,mcp",
        ],
        tmp_path,
        env,
    )
    return tmp_path / "contract-smoke", env


def _checker():
    spec = importlib.util.spec_from_file_location(
        "connector_contract_checker",
        SCRIPTS / "check_connector_contract.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_package_data_and_sdk_boundary(generated):
    root, _ = generated
    assert _checker().check_project(root, "contract_smoke") == []
    project = tomllib.loads((root / "pyproject.toml").read_text())
    package = root / "contract_smoke"
    assert not (package / "agent_server.py").exists()
    patterns = project["tool"]["setuptools"]["package-data"]["contract_smoke"]
    content = [package / "connector_manifest.yml"]
    content.extend(
        path
        for directory in ("prompts", "ontology", "skills", "connectors")
        for path in (package / directory).rglob("*")
        if path.is_file()
    )
    assert any(path.suffix == ".ttl" for path in content)
    assert any(path.name == "SKILL.md" for path in content)
    for path in content:
        relative = path.relative_to(package).as_posix()
        assert any(fnmatch.fnmatch(relative, pattern) for pattern in patterns), relative


@pytest.mark.parametrize(
    "legacy",
    [
        "from agent_utilities.mcp.server_factory import create_mcp_server\n",
        "import agent_utilities.knowledge_graph.memory.native_ingest\n",
        "import importlib\nlegacy = importlib.import_module('agent_utilities.mcp.config')\n",
    ],
)
def test_stale_au_connector_template_is_rejected(generated, legacy):
    root, env = generated
    stale = root / "contract_smoke/mcp/stale.py"
    stale.write_text(legacy, encoding="utf-8")
    violations = _checker().check_project(root, "contract_smoke")
    assert any(
        "retired connector import" in value and "stale.py" in value
        for value in violations
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "check_connector_contract.py"),
            str(root),
            "--package",
            "contract_smoke",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert "retired connector import" in result.stdout


def test_no_module_is_exempt_from_the_retired_import_rule(generated):
    root, _ = generated
    package = root / "contract_smoke"
    (package / "agent_server.py").write_text(
        "from agent_utilities.agent_server import Agent\n"
    )
    assert any(
        "agent_server.py" in error
        for error in _checker().check_project(root, "contract_smoke")
    )


LIVE_DISCOVERY = textwrap.dedent("""\
    import asyncio
    import json
    from pathlib import Path
    import socket
    import tomllib

    from fastmcp import Client
    from agent_connector_sdk.artifacts.pack import build_content_pack
    from agent_connector_sdk.artifacts.prompts import PromptArtifactKind
    from agent_connector_sdk.artifacts.resources import ResourceArtifactKind
    from agent_connector_sdk.artifacts.skills import SkillArtifactKind
    from agent_connector_sdk.artifacts.tools import ToolArtifactKind
    from agent_connector_sdk.manifest.loader import require_valid_connector_package
    from agent_connector_sdk.mcp.tool_surface import registered_tools
    from agent_connector_sdk.transports.mcp_changes import ChangeFeed
    from agent_connector_sdk.transports.mcp_session import McpClientSession
    from contract_smoke import auth
    from contract_smoke.mcp_server import build_server

    def no_network(*args, **kwargs):
        raise AssertionError("offline smoke attempted a network connection")

    socket.socket.connect = no_network
    package = Path("contract_smoke")
    declared = tomllib.loads(Path("pyproject.toml").read_text())["project"][
        "entry-points"
    ]["agent_connector_sdk.connector"]
    (fleet,) = declared
    assert require_valid_connector_package(package).connector == fleet
    server = build_server(command_args=["--transport", "stdio", "--auth-type", "none"])
    assert auth._client is None
    operation = registered_tools(server)["contract_smoke_get_system_status"]
    assert operation.tags >= {"granular", "gated", "operation"}
    assert operation.annotations.read_only_hint is True

    async def verify():
        async with Client(server) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools} == {"contract_smoke_get_system_status"}
            prompts = {prompt.name for prompt in await client.list_prompts()}
            assert {"contract_smoke_specialist"} <= prompts
            prompt = await client.get_prompt("contract_smoke_specialist")
            assert "Contract Smoke" in prompt.messages[0].content.text
            resources = {str(resource.uri) for resource in await client.list_resources()}
            expected = {
                "manifest://connector", f"ontology://{fleet}/contract-smoke.ttl",
                "skill://contract-smoke-starter/SKILL.md",
            }
            assert expected <= resources, resources
            for uri in expected:
                contents = await client.read_resource(uri)
                assert contents and contents[0].text.strip()
            for path in (package / "ontology/shapes").glob("*.ttl"):
                assert f"shapes://{fleet}/{path.name}" in resources
            manifest = await client.read_resource("manifest://connector")
            assert json.loads(manifest[0].text)["connector"] == fleet
            pack = await build_content_pack(
                McpClientSession(client, feed=ChangeFeed()),
                connector=fleet,
                kinds=(ToolArtifactKind(), SkillArtifactKind(),
                       PromptArtifactKind(), ResourceArtifactKind()),
            )
            assert pack.connector == fleet
            assert pack.server_package_version == "0.1.0"
            assert expected <= pack.resource_uris
            assert "connector://status" not in pack.resource_uris
            kinds = {entry.kind.value for entry in pack.archive.entries}
            assert {"tool", "skill", "prompt", "ontology", "manifest"} <= kinds
            entry = next(entry for entry in pack.archive.entries if entry.kind.value == "tool")
            body = json.loads(pack.archive.data[entry.body.offset:entry.body.offset + entry.body.length])
            assert body["input_schema"]["type"] == "object"
            assert body["output_schema"]["type"] == "object"
        assert auth._client is None
        print(json.dumps({"tools": len(tools), "prompts": len(prompts), "resources": len(resources), "pack_entries": len(pack.archive.entries), "pack_kinds": sorted(kinds)}))

    asyncio.run(verify())
    """)


def test_generated_server_lists_real_content_and_schema_contracts(generated):
    pytest.importorskip("agent_connector_sdk.mcp.server")
    pytest.importorskip("agent_connector_sdk.ingest")
    root, env = generated
    _run(["-c", LIVE_DISCOVERY], root, env)
    _run(["scripts/generate_tool_schemas.py"], root, env)
    _run(["scripts/generate_tool_schemas.py", "--check"], root, env)
    _run(
        [
            "-m",
            "pytest",
            "-q",
            "tests/test_kg_ingest.py",
            "tests/test_auth.py",
            "tests/test_api_wrapper.py",
            "--override-ini",
            "addopts=",
        ],
        root,
        env,
    )

"""Execute the CLI backend's generated contracts without HTTP dependencies."""

from __future__ import annotations

import ast
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
CONTEXT = {
    "pkg_dir": "cli_fixture",
    "upper_name": "CLI_FIXTURE",
    "package_name": "cli-fixture",
    "concept_prefix": "CLI",
}


@pytest.fixture(scope="module")
def templates():
    spec = importlib.util.spec_from_file_location("cli_templates", SCRIPTS / "cli_templates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_source_imports_only_sdk_config(templates):
    source = templates.CLI_PY.format(**CONTEXT)
    tree = ast.parse(source)
    modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    sdk = {name for name in modules if name and name.startswith("agent_connector_sdk")}
    assert sdk == {"agent_connector_sdk.config"}
    assert "BASE_URL" not in source
    assert "TOKEN_REF" not in source
    assert "httpx" not in source
    assert "capture_output" not in source
    assert "shell=False" in source


def test_cli_mcp_exposes_only_read_only_action(templates):
    tree = ast.parse(templates.CLI_MCP_SYSTEM_PY.format(**CONTEXT))
    tool = next(node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef))
    assert [argument.arg for argument in tool.args.args] == ["action", "client"]
    decorator = tool.decorator_list[0]
    annotations = next(item.value for item in decorator.keywords if item.arg == "annotations")
    assert ast.literal_eval(annotations) == {
        "readOnlyHint": True, "destructiveHint": False,
        "idempotentHint": True, "openWorldHint": False,
    }
    assert any(
        isinstance(node, ast.ImportFrom) and node.level == 2 and node.module == "cli"
        for node in ast.walk(tree)
    )


def test_generated_cli_runtime_contracts(templates, tmp_path):
    package = tmp_path / "cli_fixture"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "cli.py").write_text(templates.CLI_PY.format(**CONTEXT))
    # Only config is doubled: run real processes and the exact generated tests.
    sdk = tmp_path / "agent_connector_sdk"
    sdk.mkdir()
    (sdk / "__init__.py").write_text("")
    (sdk / "config.py").write_text(
        "import os\ndef load_config(): return None\n"
        "def setting(name, default=''): return os.environ.get(name, default)\n"
    )
    test_file = tmp_path / "test_cli.py"
    test_file.write_text(templates.TESTS_CLI.format(**CONTEXT))
    environment = dict(os.environ, PYTHONPATH=str(tmp_path), PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(test_file)],
        cwd=tmp_path, env=environment, capture_output=True, text=True,
        timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _require_sdk():
    if importlib.util.find_spec("agent_connector_sdk") is None:
        if os.environ.get("MCP_BUILDER_REQUIRE_SDK") == "1":
            pytest.fail("MCP_BUILDER_REQUIRE_SDK=1 requires the connector SDK", pytrace=False)
        pytest.skip("the optional real connector SDK environment is unavailable")
    importlib.import_module("agent_connector_sdk.mcp.server")
    importlib.import_module("agent_connector_sdk.manifest.loader")


@pytest.mark.parametrize("required", [False, True])
def test_sdk_requirement_is_explicit(monkeypatch, required):
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    monkeypatch.setenv("MCP_BUILDER_REQUIRE_SDK", "1" if required else "0")
    expected = pytest.fail.Exception if required else pytest.skip.Exception
    with pytest.raises(expected):
        _require_sdk()


LIVE_CLI_CONTRACT = textwrap.dedent("""\
    import asyncio
    import json
    import os
    from pathlib import Path
    import socket
    import subprocess
    import sys
    from unittest.mock import patch

    from fastmcp import Client
    from mcp import MCPError
    import pytest
    from agent_connector_sdk.manifest.loader import require_valid_connector_package
    from agent_connector_sdk.mcp.tool_surface import registered_tools
    from cli_smoke import cli
    from cli_smoke.mcp_server import build_server

    def no_network(*args, **kwargs):
        raise AssertionError("CLI smoke attempted a network connection")

    socket.socket.connect = no_network
    package = Path("cli_smoke")
    assert require_valid_connector_package(package).connector == "cli-smoke"
    assert not any(key.startswith("CLI_SMOKE_") for key in os.environ)
    with patch.object(subprocess, "Popen", side_effect=AssertionError("build invoked CLI")):
        server = build_server(command_args=["--transport", "stdio", "--auth-type", "none"])
    assert cli._client is None
    assert registered_tools(server)["system_operations"].tags >= {"granular", "gated", "system"}

    async def verify():
        async with Client(server) as client:
            with patch.object(subprocess, "Popen", side_effect=AssertionError("discovery invoked CLI")):
                tools = await client.list_tools()
                assert {tool.name for tool in tools} == {"system_operations"}
                tool = tools[0]
                assert set(tool.input_schema["properties"]) == {"action"}
                assert tool.annotations.read_only_hint is True
                assert tool.annotations.destructive_hint is False
                prompts = {item.name for item in await client.list_prompts()}
                assert {"main_agent", "cli_smoke_specialist"} <= prompts
                prompt = await client.get_prompt("main_agent")
                assert prompt.messages[0].content.text.strip()
                resources = {str(item.uri) for item in await client.list_resources()}
                expected = {
                    "manifest://connector", "ontology://cli-smoke/cli-smoke.ttl",
                    "skill://cli-smoke-starter/SKILL.md",
                }
                assert expected <= resources
                for uri in expected:
                    contents = await client.read_resource(uri)
                    assert contents and contents[0].text.strip()
                manifest = await client.read_resource("manifest://connector")
                assert json.loads(manifest[0].text)["connector"] == "cli-smoke"
            assert cli._client is None
            executable = Path("fixture-program").resolve()
            executable.write_text("#!" + sys.executable + "\\nimport sys\\nassert sys.argv[1:] == ['--version']\\nprint('fixture 1.0')\\n")
            executable.chmod(0o700)
            os.environ["CLI_SMOKE_EXECUTABLE"] = str(executable)
            result = await client.call_tool("system_operations", {"action": "status"})
            assert result.data == {"status": "ok", "version": "fixture 1.0"}
            with patch.object(subprocess, "Popen", side_effect=AssertionError("unknown action invoked CLI")):
                with pytest.raises(MCPError, match="Unsupported CLI action") as rejected:
                    await client.call_tool("system_operations", {"action": "--exec private-marker"})
            assert "private-marker" not in str(rejected.value)
            cli.close_client()
        print("CLI live tool, native content, manifest and execution contracts passed")

    asyncio.run(verify())
    """)


def _checked_python(arguments, root, env):
    result = subprocess.run(
        [sys.executable, *arguments], cwd=root, env=env, capture_output=True,
        text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_cli_server_real_sdk_contract(tmp_path):
    _require_sdk()
    if os.name != "posix":
        pytest.skip("real CLI execution requires POSIX")
    env = {key: value for key, value in os.environ.items() if not key.startswith("CLI_SMOKE_")}
    env.update({
        "MCP_FLEET_REGISTRATION": "false", "AUTH_TYPE": "none",
        "HOST": "127.0.0.1", "TRANSPORT": "stdio", "SYSTEMTOOL": "true",
        "MCP_ENABLED_TOOLS": "", "MCP_DISABLED_TOOLS": "",
        "XDG_CONFIG_HOME": str(tmp_path / "config"), "PYTHONDONTWRITEBYTECODE": "1",
    })
    _checked_python(
        [str(SCRIPTS / "scaffold_package.py"), "cli-smoke", "--output-dir", str(tmp_path),
         "--type", "cli,mcp"], tmp_path, env,
    )
    root = tmp_path / "cli-smoke"
    _checked_python(["-c", LIVE_CLI_CONTRACT], root, env)
    _checked_python(["scripts/generate_tool_schemas.py"], root, env)
    _checked_python(["scripts/generate_tool_schemas.py", "--check"], root, env)
    _checked_python([
        "-m", "pytest", "-q", "tests/test_cli.py", "--override-ini", "addopts=",
    ], root, env)

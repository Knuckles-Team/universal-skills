"""Bounded local CLI transport templates for a reviewed status-only MCP tool."""

CLI_PY = r'''
"""Run the reviewed status command, never caller-provided commands or secrets.

Configure an absolute executable path. Adding an action requires reviewing its
fixed argv, effects and output; do not place credentials in argv. This starter
accepts no operands. Execution requires POSIX; import and discovery are portable.
"""

from __future__ import annotations

import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import time
from types import MappingProxyType

from agent_connector_sdk.config import load_config, setting

_ACTIONS = MappingProxyType({{"status": ("--version",)}})
_TIMEOUT_SECONDS = 10.0
_MAX_OUTPUT_BYTES = 64 * 1024
_ENVIRONMENT = {{"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}}
_client: CliClient | None = None


class CliError(RuntimeError):
    """A caller-safe failure containing no command, output or environment data."""


def _executable(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 4096 or any(c in value for c in "\x00\r\n"):
        raise CliError("Configure a valid absolute CLI executable path")
    path = Path(value)
    if not path.is_absolute() or not path.is_file() or not os.access(path, os.X_OK):
        raise CliError("Configure a valid absolute CLI executable path")
    return str(path.resolve())


def _stop(process: subprocess.Popen) -> None:
    # Also terminate descendants retaining a pipe after the direct child exits.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass  # The process group already exited; cleanup is complete.
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        raise CliError("CLI process cleanup timed out") from None
    finally:
        process.stdout.close()
        process.stderr.close()


def _read_output(process: subprocess.Popen) -> bytes:
    deadline = time.monotonic() + _TIMEOUT_SECONDS
    output = bytearray()
    observed = 0
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, True)
        selector.register(process.stderr, selectors.EVENT_READ, False)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CliError("CLI action timed out")
            for key, _ in selector.select(remaining):
                chunk = os.read(key.fd, min(8192, _MAX_OUTPUT_BYTES - observed + 1))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                observed += len(chunk)
                if observed > _MAX_OUTPUT_BYTES:
                    raise CliError("CLI output limit exceeded")
                if key.data:
                    output.extend(chunk)
    try:
        code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        raise CliError("CLI action timed out") from None
    if code:
        raise CliError("CLI action failed")
    return bytes(output)


def _invoke(executable: str, arguments: tuple[str, ...]) -> bytes:
    if os.name != "posix":
        raise CliError("CLI execution requires POSIX")
    with tempfile.TemporaryDirectory(prefix="connector-cli-") as directory:
        try:
            process = subprocess.Popen(
                [executable, *arguments], shell=False, env=dict(_ENVIRONMENT),
                cwd=directory, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True, bufsize=0,
            )
        except OSError:
            raise CliError("CLI executable could not start") from None
        try:
            return _read_output(process)
        except OSError:
            raise CliError("CLI output could not be read") from None
        finally:
            _stop(process)


class CliClient:
    """Validate configuration without executing a process during construction."""

    def __init__(self, executable: str) -> None:
        self._executable = _executable(executable)

    def run(self, action: str) -> dict[str, str]:
        if not isinstance(action, str) or action not in _ACTIONS:
            raise CliError("Unsupported CLI action")
        output = _invoke(self._executable, _ACTIONS[action])
        return {{"status": "ok", "version": output.decode("utf-8", errors="replace").strip()}}

    def get_system_status(self) -> dict[str, str]:
        """Read the configured program's version using the fixed status action."""
        return self.run("status")


def get_client() -> CliClient:
    """Resolve operator configuration lazily; no HTTP or credential settings."""
    global _client
    if _client is None:
        load_config()
        _client = CliClient(setting("{upper_name}_EXECUTABLE", ""))
    return _client


def close_client() -> None:
    """Forget configuration; each command owns and closes its process resources."""
    global _client
    _client = None
'''

CLI_MCP_SYSTEM_PY = r'''
"""A read-only reviewed CLI action, with no command or argument tool input."""

from agent_connector_sdk.mcp.action_dispatch import resolve_action
from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ..cli import CliError, get_client


def register_system_tools(mcp: FastMCP):
    @mcp.tool(
        tags={{"system"}},
        annotations={{"readOnlyHint": True, "destructiveHint": False,
                     "idempotentHint": True, "openWorldHint": False}},
    )
    async def system_operations(action: str = "status", client=Depends(get_client)) -> dict:
        """Read the configured CLI version. CONCEPT:{concept_prefix}-001"""
        try:
            resolved = resolve_action(action, {{"status"}}, service="{package_name}")
        except ValueError:
            raise CliError("Unsupported CLI action") from None
        if isinstance(resolved, dict):
            return resolved
        return await run_blocking(client.get_system_status)
'''

TESTS_CLI = r'''
"""Real isolated subprocess contracts; no provider, network or credential use."""

import importlib
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest

from {pkg_dir} import cli


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch):
    cli.close_client()
    monkeypatch.setattr(cli, "load_config", lambda: None)
    monkeypatch.setattr(cli, "setting", lambda name, default="": os.environ.get(name, default))
    monkeypatch.delenv("{upper_name}_EXECUTABLE", raising=False)
    yield
    cli.close_client()


@pytest.fixture
def executable(tmp_path):
    if os.name != "posix":
        pytest.skip("real executable fixture requires POSIX")

    def make(body, name="fixture"):
        path = tmp_path / name
        path.write_text("#!" + sys.executable + "\n" + body, encoding="utf-8")
        path.chmod(0o700)
        return str(path)
    return make


def test_import_and_client_construction_do_not_execute(monkeypatch):
    path = sys.executable
    monkeypatch.setattr(cli.subprocess, "Popen", lambda *a, **k: pytest.fail("process started"))
    importlib.reload(cli)
    monkeypatch.setattr(cli, "load_config", lambda: None)
    monkeypatch.setattr(cli, "setting", lambda *a: path)
    assert isinstance(cli.get_client(), cli.CliClient)
    assert cli.get_client() is cli.get_client()


def test_missing_executable_configuration_is_safe():
    with pytest.raises(cli.CliError, match="absolute CLI executable"):
        cli.get_client()


@pytest.mark.parametrize("value", ["", "relative", "--help", "/missing/fixture", "bad\npath"])
def test_invalid_executable_rejected(value):
    with pytest.raises(cli.CliError, match="absolute CLI executable"):
        cli.CliClient(value)


@pytest.mark.skipif(os.name != "posix", reason="POSIX executable mode contract")
def test_nonexecutable_file_rejected(tmp_path):
    path = tmp_path / "not-executable"
    path.write_text("untrusted")
    with pytest.raises(cli.CliError, match="absolute CLI executable"):
        cli.CliClient(str(path))


def test_fixed_argv_treats_metacharacters_literally(executable, tmp_path):
    path = executable("import json, sys\nprint(json.dumps(sys.argv[1:]))\n", "literal;$(touch injected)")
    result = cli.CliClient(path).get_system_status()
    assert json.loads(result["version"]) == ["--version"]
    assert not (tmp_path / "injected").exists()


@pytest.mark.parametrize("action", ["--exec", "status;touch injected", "$(id)", "status --help", None])
def test_unreviewed_actions_rejected_without_execution(executable, monkeypatch, action):
    client = cli.CliClient(executable("raise AssertionError('must not execute')\n"))
    monkeypatch.setattr(cli.subprocess, "Popen", lambda *a, **k: pytest.fail("process started"))
    with pytest.raises(cli.CliError, match="Unsupported CLI action"):
        client.run(action)


def test_child_environment_excludes_ambient_credentials(executable, monkeypatch):
    monkeypatch.setenv("SCAFFOLD_TEST_SECRET", "private-value")
    path = executable("import json, os\nprint(json.dumps(dict(os.environ)))\n")
    environment = json.loads(cli.CliClient(path).get_system_status()["version"])
    assert "SCAFFOLD_TEST_SECRET" not in environment
    assert "HOME" not in environment
    assert environment["PATH"] == "/usr/bin:/bin"


def test_nonzero_exit_does_not_echo_output(executable):
    path = executable("import sys\nprint('private-stdout')\nprint('private-stderr', file=sys.stderr)\nsys.exit(9)\n")
    with pytest.raises(cli.CliError) as error:
        cli.CliClient(path).get_system_status()
    assert str(error.value) == "CLI action failed"


def test_stderr_is_not_returned_on_success(executable):
    path = executable("import sys\nprint('version 1')\nprint('private-stderr', file=sys.stderr)\n")
    assert cli.CliClient(path).get_system_status() == {{"status": "ok", "version": "version 1"}}


def test_deleted_executable_has_safe_start_failure(executable):
    path = executable("print('version 1')\n")
    client = cli.CliClient(path)
    Path(path).unlink()
    with pytest.raises(cli.CliError, match="^CLI executable could not start$"):
        client.get_system_status()


def test_timeout_stops_a_silent_process(executable, monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_TIMEOUT_SECONDS", 0.2)
    pid_file = tmp_path / "child.pid"
    path = executable(
        "import os, time\nfrom pathlib import Path\nPath(" + repr(str(pid_file))
        + ").write_text(str(os.getpid()))\ntime.sleep(20)\n"
    )
    started = time.monotonic()
    with pytest.raises(cli.CliError, match="timed out"):
        cli.CliClient(path).get_system_status()
    assert time.monotonic() - started < 3
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_file.read_text()), 0)


@pytest.mark.parametrize("descriptor", [1, 2])
def test_stdout_and_stderr_share_a_finite_output_cap(executable, monkeypatch, descriptor):
    monkeypatch.setattr(cli, "_MAX_OUTPUT_BYTES", 1024)
    path = executable("import os\nwhile True: os.write(" + str(descriptor) + ", b'x' * 4096)\n")
    with pytest.raises(cli.CliError, match="output limit"):
        cli.CliClient(path).get_system_status()


def test_combined_output_is_bounded(executable, monkeypatch):
    monkeypatch.setattr(cli, "_MAX_OUTPUT_BYTES", 1024)
    path = executable("import os\nos.write(1, b'x' * 600)\nos.write(2, b'y' * 600)\n")
    with pytest.raises(cli.CliError, match="output limit"):
        cli.CliClient(path).get_system_status()


def test_unsupported_platform_fails_before_start(monkeypatch):
    client = cli.CliClient(sys.executable)
    monkeypatch.setattr(cli, "os", SimpleNamespace(name="nt"))
    with pytest.raises(cli.CliError, match="requires POSIX"):
        client.get_system_status()
'''

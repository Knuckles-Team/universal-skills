"""mcp-client-onboarder resolves the Graph OS config root (one-release fallback)."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / (
    "universal_skills/infrastructure/mcp-client-onboarder/scripts"
)


def _load(name):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(
            f"_cfg_{name}", str(SCRIPTS / f"{name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


@pytest.fixture(autouse=True)
def _isolated(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    monkeypatch.delenv("GRAPH_OS_CONFIG_DIR", raising=False)
    monkeypatch.delenv("AGENT_UTILITIES_CONFIG_DIR", raising=False)


@pytest.mark.parametrize("name", ["onboard", "reap"])
def test_env_override(monkeypatch, tmp_path, name):
    monkeypatch.setenv("GRAPH_OS_CONFIG_DIR", str(tmp_path / "custom"))
    assert _load(name)._CONFIG_ROOT == tmp_path / "custom"


@pytest.mark.parametrize("name", ["onboard", "reap"])
def test_new_path_wins(tmp_path, name):
    (tmp_path / "xdg" / "graph-os" / "mcp-multiplexer").mkdir(parents=True)
    (tmp_path / "xdg" / "agent-utilities" / "mcp-multiplexer").mkdir(parents=True)
    assert _load(name)._CONFIG_ROOT == tmp_path / "xdg" / "graph-os"


@pytest.mark.parametrize("name", ["onboard", "reap"])
def test_legacy_fallback_warns(tmp_path, capsys, name):
    (tmp_path / "xdg" / "agent-utilities" / "mcp-multiplexer").mkdir(parents=True)
    assert _load(name)._CONFIG_ROOT == tmp_path / "xdg" / "agent-utilities"
    err = capsys.readouterr().err
    assert "deprecated config location" in err
    assert str(tmp_path / "xdg" / "graph-os") in err


@pytest.mark.parametrize("name", ["onboard", "reap"])
def test_neither_present(tmp_path, capsys, name):
    assert _load(name)._CONFIG_ROOT == tmp_path / "xdg" / "graph-os"
    assert capsys.readouterr().err == ""

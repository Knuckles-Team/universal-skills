"""CI uses only trusted, working interpreters at the declared Python minimum."""

import importlib.util
import json
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).parents[1] / "universal_skills/agent-tools/mcp-builder/scripts"


@pytest.fixture
def selector(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "python_selector", SCRIPTS / "select_python.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path / "provisioned"
    root.mkdir()
    monkeypatch.setattr(module, "PROVISIONED_ROOT", root)
    return module


def candidate(selector, version):
    path = selector.PROVISIONED_ROOT / version / "bin/python3.12"
    path.parent.mkdir(parents=True)
    path.touch()
    return path


def test_selects_highest_usable_exact_patch_only(selector, monkeypatch):
    candidate(selector, "3.12.9")
    expected = candidate(selector, "3.12.14")
    candidate(selector, "3.12.15")
    candidate(selector, "3.13.99")
    candidate(selector, "3.12.not-a-version")
    monkeypatch.setattr(selector, "trusted_path", lambda path: True)
    calls = []

    def run(command, **options):
        calls.append(Path(command[0]))
        assert command[1:4] == ["-I", "-B", "-c"]
        assert options["timeout"] == 10
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"version": [3, 12, 14], "implementation": "cpython"}),
        )

    monkeypatch.setattr(selector.subprocess, "run", run)
    assert selector.select_python("3.12") == expected
    assert [path.parents[1].name for path in calls] == ["3.12.15", "3.12.14"]


@pytest.mark.parametrize("failure", ["startup", "json", "implementation", "timeout"])
def test_unusable_interpreter_fails_without_export(
    selector, monkeypatch, tmp_path, failure
):
    path = candidate(selector, "3.12.14")
    monkeypatch.setattr(selector, "trusted_path", lambda path: True)

    def run(*args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(str(path), 10)
        stdout = (
            "not-json"
            if failure == "json"
            else json.dumps({"version": [3, 12, 14], "implementation": "pypy"})
        )
        return SimpleNamespace(
            returncode=127 if failure == "startup" else 0, stdout=stdout
        )

    monkeypatch.setattr(selector.subprocess, "run", run)
    output = tmp_path / "github-path"
    output.write_text("existing\n")
    monkeypatch.setenv("GITHUB_PATH", str(output))
    monkeypatch.setattr(selector, "project_inputs", lambda root: ({}, [], "3.12"))
    with pytest.raises(ValueError, match="No usable administrator-provisioned"):
        selector.main()
    assert output.read_text() == "existing\n"


def test_untrusted_candidate_is_never_executed(selector, monkeypatch):
    candidate(selector, "3.12.14")
    monkeypatch.setattr(
        selector, "trusted_path", lambda path: path == selector.PROVISIONED_ROOT
    )
    monkeypatch.setattr(
        selector.subprocess, "run", lambda *a, **k: pytest.fail("Untrusted execution")
    )
    with pytest.raises(ValueError, match="No usable"):
        selector.select_python("3.12")


@pytest.mark.parametrize(
    "uid,mode,expected",
    [
        (0, 0o755, True),
        (1, 0o755, False),
        (0, 0o775, False),
        (0, stat.S_IFLNK | 0o755, False),
    ],
)
def test_trust_requires_root_ownership_no_shared_write_or_links(
    selector, monkeypatch, uid, mode, expected
):
    monkeypatch.setattr(
        Path, "lstat", lambda path: SimpleNamespace(st_uid=uid, st_mode=mode)
    )
    assert selector.trusted_path(Path("/opt/python/3.12.14/bin/python3.12")) is expected


@pytest.mark.parametrize("floor", ["3.12", "3.13"])
def test_declared_floor_and_job_scoped_path(selector, monkeypatch, tmp_path, floor):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    monkeypatch.setattr(selector, "__file__", str(scripts / "select_python.py"))
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nrequires-python = ">={floor}, <3.15"\n[project.optional-dependencies]\ntest = []\n'
    )
    (tmp_path / "uv.lock").write_text("package = []\n")
    selected = Path(f"/opt/python/{floor}.14/bin/python{floor}")
    calls = []

    def select(value):
        calls.append(value)
        return selected

    monkeypatch.setattr(selector, "select_python", select)
    output = tmp_path / "github-path"
    monkeypatch.setenv("GITHUB_PATH", str(output))
    selector.main()
    assert calls == [floor]
    assert output.read_text() == str(selected.parent) + "\n"


def test_real_startup_and_standard_library_probe(selector, monkeypatch):
    monkeypatch.setattr(selector, "trusted_path", lambda path: True)
    assert selector.usable(Path(sys.executable), tuple(sys.version_info[:3]))
    assert not selector.usable(Path(sys.executable), (3, 99, 0))


def test_missing_provisioned_root_fails_closed(selector, monkeypatch):
    monkeypatch.setattr(
        selector, "PROVISIONED_ROOT", Path("/nonexistent-provisioned-python")
    )
    with pytest.raises(
        ValueError, match="Trusted provisioned Python directory is unavailable"
    ):
        selector.select_python("3.12")

"""The missing-tool contract every repository gate follows."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "us_gate_env", Path(__file__).resolve().parents[1] / "scripts" / "gate_env.py"
)
assert _SPEC is not None and _SPEC.loader is not None
gate_env = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(gate_env)


@pytest.mark.parametrize("ci, expected", [(None, 0), ("true", 2)])
def test_missing_tool_skips_locally_and_cannot_run_in_ci(
    monkeypatch, capsys, ci, expected
) -> None:
    monkeypatch.delenv("CI", raising=False)
    if ci:
        monkeypatch.setenv("CI", ci)

    code = gate_env.main(["--gate", "demo", "--need", "no-such-tool-xyz", "--", "true"])

    assert code == expected
    out = capsys.readouterr()
    assert ("CANNOT RUN" in out.err) if ci else out.out.startswith("SKIPPED (demo): ")


@pytest.mark.parametrize("ci, expected", [(None, 0), ("1", 2)])
def test_missing_project_env_is_not_a_pass(
    tmp_path: Path, monkeypatch, capsys, ci, expected
) -> None:
    monkeypatch.delenv("CI", raising=False)
    if ci:
        monkeypatch.setenv("CI", ci)
    monkeypatch.setattr(gate_env, "project_bin", lambda: tmp_path / "absent")

    assert gate_env.main(["--gate", "demo", "--project-env", "--", "true"]) == expected
    out = capsys.readouterr()
    assert "scripts/bootstrap.sh" in (out.err if ci else out.out)


def test_project_env_leads_path_and_propagates_exit_code(
    tmp_path: Path, monkeypatch
) -> None:
    venv_bin = tmp_path / "bin"
    venv_bin.mkdir()
    tool = venv_bin / "only-in-venv"
    tool.write_text("#!/bin/sh\nexit 3\n")
    tool.chmod(0o755)
    monkeypatch.setattr(gate_env, "project_bin", lambda: venv_bin)

    assert gate_env.main(["--gate", "demo", "--project-env", "--", "only-in-venv"]) == 3

"""Security regression tests for the standalone DOCX tracked-change helper."""

from __future__ import annotations

import importlib.util
import stat
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = (
    PROJECT_ROOT
    / "universal_skills"
    / "docs"
    / "document-tools"
    / "scripts"
    / "docx_scripts"
)


@pytest.fixture
def accept_changes_module(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(
        "_test_accept_changes_security", SCRIPT_DIR / "accept_changes.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_macro_profile_is_private_and_not_shared(
    accept_changes_module, monkeypatch, tmp_path
):
    commands: list[list[str]] = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(accept_changes_module.subprocess, "run", fake_run)
    profile = tmp_path / "private-profile"

    assert accept_changes_module._setup_libreoffice_macro(profile) is True
    macro = profile / "user" / "basic" / "Standard" / "Module1.xba"
    assert macro.is_file()
    assert stat.S_IMODE(macro.stat().st_mode) == 0o600
    assert commands and profile.resolve().as_uri() in commands[0][2]


def test_symlink_input_and_output_are_rejected_without_path_disclosure(
    accept_changes_module, tmp_path
):
    source = tmp_path / "source.docx"
    source.write_bytes(b"placeholder")
    source_link = tmp_path / "source-link.docx"
    source_link.symlink_to(source)

    _, input_message = accept_changes_module.accept_changes(
        str(source_link), str(tmp_path / "out.docx")
    )
    assert input_message == "Error: configured input file was not found"
    assert str(tmp_path) not in input_message

    output_link = tmp_path / "out-link.docx"
    output_link.symlink_to(tmp_path / "elsewhere.docx")
    _, output_message = accept_changes_module.accept_changes(
        str(source), str(output_link)
    )
    assert output_message == "Error: configured output path is not a regular file"
    assert str(tmp_path) not in output_message


def test_timeout_is_failure_and_does_not_disclose_paths(
    accept_changes_module, monkeypatch, tmp_path
):
    source = tmp_path / "source.docx"
    source.write_bytes(b"placeholder")
    output = tmp_path / "output.docx"
    monkeypatch.setattr(
        accept_changes_module, "_setup_libreoffice_macro", lambda _profile: True
    )

    def timeout(*_args, **_kwargs):
        raise accept_changes_module.subprocess.TimeoutExpired("soffice", 30)

    monkeypatch.setattr(accept_changes_module.subprocess, "run", timeout)
    _, message = accept_changes_module.accept_changes(str(source), str(output))

    assert message == "Error: LibreOffice conversion timed out"
    assert str(tmp_path) not in message

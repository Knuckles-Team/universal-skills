"""Reject changed theme snapshots and preserve existing project-owned assets."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)


@pytest.fixture
def theme(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "mcp_builder_theme_under_test", SCRIPTS / "docs_assets.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "theme"
    shutil.copytree(module.SOURCE, source)
    monkeypatch.setattr(module, "SOURCE", source)
    return module


def test_theme_provenance_rejects_revision_and_content_tampering(theme):
    assert theme.verified_source() == theme.SOURCE
    manifest = theme.SOURCE / "provenance.json"
    original = manifest.read_text()
    data = json.loads(original)
    data["revision"] = "0" * 40
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="revision disagrees"):
        theme.verified_source()
    manifest.write_text(original)
    stylesheet = theme.SOURCE / "templates/mkdocs-theme/extra.css"
    stylesheet.write_bytes(stylesheet.read_bytes() + b"\n/* unreviewed change */\n")
    with pytest.raises(ValueError, match="snapshot differs"):
        theme.verified_source()


def test_theme_provenance_rejects_escape_and_symlink_sources(theme, tmp_path):
    manifest = theme.SOURCE / "provenance.json"
    original = manifest.read_text()
    outside = tmp_path / "outside.css"
    outside.write_text("/* file outside the reviewed snapshot */\n")
    data = json.loads(original)
    data["files"]["../outside.css"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="escapes its source"):
        theme.verified_source()
    manifest.write_text(original)
    stylesheet = theme.SOURCE / "templates/mkdocs-theme/extra.css"
    outside.write_bytes(stylesheet.read_bytes())
    stylesheet.unlink()
    stylesheet.symlink_to(outside)
    with pytest.raises(ValueError, match="escapes its source"):
        theme.verified_source()
    assert outside.read_bytes() == stylesheet.read_bytes()


def test_generator_refuses_different_theme_without_overwriting_it(tmp_path):
    command = [
        sys.executable,
        str(SCRIPTS / "scaffold_package.py"),
        "theme-contract",
        "--output-dir",
        str(tmp_path),
    ]
    first = subprocess.run(
        command, capture_output=True, text=True, timeout=30, check=False
    )
    assert first.returncode == 0, first.stdout + first.stderr
    root = tmp_path / "theme-contract"
    stylesheet = root / "docs/stylesheets/extra.css"
    preserved = b"/* project-owned stylesheet; must survive generator re-runs */\n"
    stylesheet.write_bytes(preserved)
    snapshot = root / ".pipeline-theme/templates/mkdocs-theme/extra.css"
    canonical = snapshot.read_bytes()
    second = subprocess.run(
        command, capture_output=True, text=True, timeout=30, check=False
    )
    assert second.returncode != 0
    assert "preserved existing" in second.stdout
    assert stylesheet.read_bytes() == preserved
    assert snapshot.read_bytes() == canonical

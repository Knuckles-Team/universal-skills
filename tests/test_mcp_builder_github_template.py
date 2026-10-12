"""All-file substitutions and API mutation boundaries use deterministic fixtures."""

import sys
import importlib
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
template = importlib.import_module("github_template")


def test_hidden_files_and_one_pass_substitutions(tmp_path):
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github/config").write_text("old_pkg old old_pkg")
    (tmp_path / "old_pkg").mkdir()
    (tmp_path / "old_pkg/__init__.py").write_text("old_pkg")
    source = template.files(tmp_path)
    result = template.substitute(source, {"old_pkg": "new_pkg", "old": "old_pkg"})
    assert result[".github/config"] == b"new_pkg old_pkg new_pkg"
    assert result["new_pkg/__init__.py"] == b"new_pkg"
    assert template.verify(result, dict(result), set())["unexpected"] == []
    changed = {**result, ".github/config": b"drift"}
    assert template.verify(result, changed, set())["unexpected"] == [".github/config"]


def test_refuses_secret_file_and_existing_target(tmp_path):
    (tmp_path / ".env").write_text("EXAMPLE=value")
    with pytest.raises(ValueError, match="secret-bearing"):
        template.files(tmp_path)


def test_hash_bound_checks_before_remote_write(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("safe template")
    monkeypatch.setattr(
        template, "api", lambda *args: pytest.fail("unchecked files reached remote API")
    )
    with pytest.raises(ValueError, match="exact complete"):
        template.publish_template(
            tmp_path, "Example", "example-template", {"passed": True, "files": {}}
        )


def test_generate_uses_private_template_api_and_frozen_head(monkeypatch):
    seen = []
    monkeypatch.setattr(template, "preflight", lambda owner, name: None)

    def api(route, method="GET", data=None):
        seen.append((route, method, data))
        if route == "repos/Example/template":
            return {"is_template": True, "default_branch": "main"}
        if route.endswith("/commits/main"):
            return {"sha": "a" * 40}
        assert route == "repos/Example/template/generate"
        return {"full_name": "Example/connector", "private": True}

    monkeypatch.setattr(template, "api", api)
    result = template.create_from_template(
        "Example", "connector", "Example/template", "a" * 40
    )
    assert result["private"]
    write = next(item for item in seen if item[1] == "POST")
    assert write[2] == {
        "owner": "Example",
        "name": "connector",
        "private": True,
        "include_all_branches": False,
    }

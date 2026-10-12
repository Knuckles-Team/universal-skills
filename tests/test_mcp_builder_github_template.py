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
    monkeypatch.setattr(
        template,
        "commit_tree",
        lambda repo, sha: [("README.md", "100644", "blob", "fixture")],
    )

    def api(route, method="GET", data=None):
        seen.append((route, method, data))
        if route in {"repos/Example/template", "repos/Example/connector"}:
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


@pytest.mark.parametrize(
    "replacement",
    ["a//b", "a/./b", "../outside", "/outside", "a\\b", ".git/config", "a/../b"],
)
def test_unsafe_substituted_paths_fail_before_writes(tmp_path, replacement):
    source = tmp_path / "source"
    source.mkdir()
    (source / "old").write_text("fixture")
    target = tmp_path / "target"
    with pytest.raises(ValueError, match="unsafe|noncanonical"):
        template.render(source, target, {"old": replacement})
    assert not target.exists()


def test_duplicate_and_file_directory_collisions_fail():
    with pytest.raises(ValueError, match="duplicate"):
        template.substitute({"one": b"1", "two": b"2"}, {"one": "same", "two": "same"})
    with pytest.raises(ValueError, match="collision"):
        template.substitute(
            {"one": b"1", "two": b"2"}, {"one": "same", "two": "same/file"}
        )


def test_executable_mode_preserved_and_bound_to_checks(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    script = source / "old.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    script.chmod(0o755)
    (source / "README.md").write_text("fixture")
    target = tmp_path / "target"
    record = template.render(source, target, {"old": "new"})
    assert (target / "new.sh").stat().st_mode & 0o111
    assert record["new.sh"]["mode"] == "100755"
    (target / "new.sh").chmod(0o644)
    monkeypatch.setattr(
        template, "api", lambda *args: pytest.fail("mode drift reached API")
    )
    with pytest.raises(ValueError, match="exact complete"):
        template.publish_template(
            target, "Example", "example-template", {"passed": True, "files": record}
        )


@pytest.mark.parametrize("failure", ["branch", "tree"])
def test_generated_repository_attestation_rejects_drift(monkeypatch, failure):
    monkeypatch.setattr(template, "preflight", lambda *args: None)
    source_reads = 0

    def api(route, method="GET", data=None):
        nonlocal source_reads
        if route == "repos/Example/template":
            source_reads += 1
            return {
                "is_template": True,
                "default_branch": "other"
                if failure == "branch" and source_reads > 1
                else "main",
            }
        if "/commits/" in route:
            return {"sha": "a" * 40}
        if route.endswith("/generate"):
            return {"full_name": "Example/connector", "private": True}
        if route == "repos/Example/connector":
            return {"default_branch": "main"}
        pytest.fail(route)

    monkeypatch.setattr(template, "api", api)
    monkeypatch.setattr(
        template,
        "commit_tree",
        lambda repo, sha: [
            (
                "README",
                "100644",
                "blob",
                "changed"
                if failure == "tree" and repo.endswith("connector")
                else "same",
            )
        ],
    )
    with pytest.raises(RuntimeError, match="preserved"):
        template.create_from_template(
            "Example", "connector", "Example/template", "a" * 40
        )

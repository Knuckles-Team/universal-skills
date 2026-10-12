"""Publish one complete locally checked tree without remote template access."""

import base64
import importlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
publisher = importlib.import_module("github_publish")


@pytest.fixture
def source(tmp_path):
    (tmp_path / "README.md").write_text("reviewed README\n")
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github/config.yml").write_text("name: checked\n")
    (tmp_path / "asset.bin").write_bytes(b"\xff\x00\x01")
    (tmp_path / "run.sh").write_text("#!/bin/sh\nexit 0\n")
    (tmp_path / "run.sh").chmod(0o755)
    return tmp_path


class GitHub:
    """Git data fixture with complete tree readback and deliberate drift cases."""

    def __init__(self, source, drift=None):
        self.source, self.drift = source, drift
        self.seen, self.entries = [], []
        self.head = "parent"

    def __call__(self, route, method="GET", data=None):
        self.seen.append((route, method, data))
        if route == "orgs/Example/repos":
            assert data == {
                "name": "connector",
                "private": True,
                "is_template": False,
                "auto_init": False,
            }
            # Freeze before the first remote call: subsequent edits are unreviewed.
            (self.source / "README.md").write_text("concurrent unreviewed edit")
            (self.source / "run.sh").chmod(0o644)
            return {
                "private": self.drift != "visibility",
                "is_template": False,
                "full_name": "Example/connector",
                "default_branch": "main",
                "id": 1234,
            }
        assert route.startswith("repos/Example/connector"), route
        if route.endswith("/contents/README.md"):
            assert base64.b64decode(data["content"]) == b"reviewed README\n"
            assert data["branch"] == "main"
            if self.drift == "seed":
                self.head = "concurrent-commit"
            return {
                "commit": {
                    "sha": "parent",
                    "parents": [{"sha": "concurrent-commit"}]
                    if self.drift == "before_init"
                    else [],
                }
            }
        if route == "repos/Example/connector":
            phase = "early" if self.head == "parent" else "final"
            return {
                "id": 5678 if self.drift == f"{phase}_identity" else 1234,
                "full_name": "Other/connector"
                if self.drift == f"{phase}_name"
                else "Example/connector",
                "private": self.drift != f"{phase}_visibility",
                "is_template": self.drift == f"{phase}_template",
                "default_branch": "other"
                if self.drift == "early_branch"
                or (self.drift == "branch" and self.head != "parent")
                else "main",
            }
        if route.endswith("/git/ref/heads/main"):
            return {"object": {"sha": self.head}}
        if route.endswith("/git/blobs"):
            return {
                "sha": "bad"
                if self.drift == "blob"
                else publisher.blob_sha(base64.b64decode(data["content"]))
            }
        if route.endswith("/git/trees"):
            for entry in data["tree"]:
                assert entry["type"] == "blob"
                sha = entry.get("sha") or publisher.blob_sha(entry["content"].encode())
                self.entries.append(
                    {key: entry[key] for key in ("path", "mode", "type")} | {"sha": sha}
                )
            return {"sha": "tree"}
        if route.endswith("/git/commits"):
            assert data["parents"] == ["parent"]
            return {"sha": "commit"}
        if route.endswith("/git/commits/commit"):
            return {"tree": {"sha": "tree"}}
        if route.endswith("/git/trees/tree?recursive=1"):
            entries = list(self.entries)
            if self.drift == "tree":
                entries[0] = {**entries[0], "mode": "120000"}
            if self.drift == "missing":
                entries.pop()
            if self.drift == "added":
                entries.append(
                    {
                        "path": "unexpected",
                        "mode": "100644",
                        "type": "blob",
                        "sha": "bad",
                    }
                )
            return {"tree": entries, "truncated": self.drift == "truncated"}
        if route.endswith("/git/refs/heads/main"):
            assert data == {"sha": "commit", "force": False}
            self.head = "other" if self.drift == "head" else "commit"
            return {}
        pytest.fail(f"Unexpected API operation: {route}")


def run_publish(source, monkeypatch, drift=None):
    checks = {"passed": True, "files": publisher.manifest(source)}
    remote = GitHub(source, drift)
    monkeypatch.setattr(publisher, "api", remote)
    monkeypatch.setattr(publisher, "preflight", lambda *args: "orgs/Example/repos")
    return remote, checks


def test_publish_attests_frozen_complete_tree_without_template(source, monkeypatch):
    remote, checks = run_publish(source, monkeypatch)
    result = publisher.publish(source, "Example", "connector", checks, "Operator")
    assert result == {
        "repository": "Example/connector",
        "sha": "commit",
        "private": True,
        "files": checks["files"],
    }
    assert publisher.manifest(source) != checks["files"]
    assert {item["path"] for item in remote.entries} == set(checks["files"])
    assert (
        next(item for item in remote.entries if item["path"] == "run.sh")["mode"]
        == "100755"
    )
    assert all(
        "/generate" not in route and "template" not in route
        for route, _, _ in remote.seen
    )
    assert all(method != "DELETE" for _, method, _ in remote.seen)


@pytest.mark.parametrize(
    "drift",
    ["visibility", "blob", "tree", "missing", "added", "truncated", "branch", "head"],
)
def test_remote_drift_fails_without_delete_or_retry(source, monkeypatch, drift):
    remote, checks = run_publish(source, monkeypatch, drift)
    with pytest.raises((ValueError, RuntimeError), match="preserved"):
        publisher.publish(source, "Example", "connector", checks, "Operator")
    writes = [(route, method) for route, method, _ in remote.seen if method != "GET"]
    assert len(writes) == len(set(writes))
    assert all(method != "DELETE" for _, method in writes)
    if drift not in {"branch", "head"}:
        assert not any(method == "PATCH" for _, method in writes)


@pytest.mark.parametrize("drift", ["before_init", "seed", "early_branch"])
def test_initialization_drift_is_never_adopted_as_publication_parent(
    source, monkeypatch, drift
):
    remote, checks = run_publish(source, monkeypatch, drift)
    with pytest.raises(RuntimeError, match="initialization; preserved"):
        publisher.publish(source, "Example", "connector", checks, "Operator")
    writes = [(route, method) for route, method, _ in remote.seen if method != "GET"]
    assert writes == [
        ("orgs/Example/repos", "POST"),
        ("repos/Example/connector/contents/README.md", "PUT"),
    ]
    assert remote.entries == []


@pytest.mark.parametrize("phase", ["early", "final"])
@pytest.mark.parametrize("field", ["identity", "name", "visibility", "template"])
def test_repository_policy_and_identity_are_rechecked(
    source, monkeypatch, phase, field
):
    remote, checks = run_publish(source, monkeypatch, f"{phase}_{field}")
    with pytest.raises(RuntimeError, match="identity or visibility changed; preserved"):
        publisher.publish(source, "Example", "connector", checks, "Operator")
    writes = [(route, method) for route, method, _ in remote.seen if method != "GET"]
    if phase == "early":
        assert writes == [
            ("orgs/Example/repos", "POST"),
            ("repos/Example/connector/contents/README.md", "PUT"),
        ]
        assert remote.entries == []
    else:
        assert writes[-1] == ("repos/Example/connector/git/refs/heads/main", "PATCH")
    assert all(method != "DELETE" for _, method in writes)


@pytest.mark.parametrize("drift", ["content", "mode", "added", "removed", "failed"])
def test_checks_bind_every_file_and_mode_before_remote_calls(
    source, monkeypatch, drift
):
    checks = {"passed": True, "files": publisher.manifest(source)}
    if drift == "content":
        (source / "README.md").write_text("changed")
    elif drift == "mode":
        (source / "run.sh").chmod(0o644)
    elif drift == "added":
        (source / ".added").write_text("changed")
    elif drift == "removed":
        (source / "asset.bin").unlink()
    else:
        checks["passed"] = False
    monkeypatch.setattr(
        publisher, "api", lambda *args: pytest.fail("unchecked source reached API")
    )
    with pytest.raises(ValueError, match="exact complete"):
        publisher.publish(source, "Example", "connector", checks, "Operator")


@pytest.mark.parametrize("kind", ["secret", "symlink", "empty", "missing"])
def test_invalid_local_source_rejected(tmp_path, kind):
    if kind == "secret":
        (tmp_path / ".env").write_text("EXAMPLE=value")
    elif kind == "symlink":
        (tmp_path / "link").symlink_to("README.md")
    elif kind == "missing":
        tmp_path /= "absent"
    with pytest.raises(ValueError):
        publisher.manifest(tmp_path)


@pytest.mark.parametrize(
    "owner,kind,route",
    [
        ("Example", "Organization", "orgs/Example/repos"),
        ("Operator", "User", "user/repos"),
    ],
)
def test_preflight_supports_explicit_actor_and_normal_owner(
    monkeypatch, owner, kind, route
):
    monkeypatch.setattr(
        publisher,
        "api",
        lambda path: {"login": "Operator"} if path == "user" else {"type": kind},
    )
    monkeypatch.setattr(
        publisher.subprocess,
        "run",
        lambda *args, **kw: SimpleNamespace(returncode=1, stderr="HTTP 404"),
    )
    assert publisher.preflight(owner, "connector", "operator") == route


@pytest.mark.parametrize("failure", ["actor", "owner", "exists", "unknown", "path"])
def test_preflight_fails_closed(monkeypatch, failure):
    monkeypatch.setattr(
        publisher,
        "api",
        lambda route: (
            {"login": "Other" if failure == "actor" else "Operator"}
            if route == "user"
            else {"type": "User" if failure == "owner" else "Organization"}
        ),
    )
    monkeypatch.setattr(
        publisher.subprocess,
        "run",
        lambda *args, **kw: SimpleNamespace(
            returncode=0 if failure == "exists" else 1,
            stderr="HTTP 503" if failure == "unknown" else "HTTP 404",
        ),
    )
    with pytest.raises((ValueError, PermissionError, FileExistsError)):
        publisher.preflight(
            "../Example" if failure == "path" else "Example", "connector", "Operator"
        )


def test_manifest_command_is_local_and_does_not_certify_checks(
    source, monkeypatch, capsys
):
    monkeypatch.setattr(
        publisher, "api", lambda *args: pytest.fail("manifest contacted GitHub")
    )
    monkeypatch.setattr(sys, "argv", ["github_publish.py", "manifest", str(source)])
    publisher.main()
    result = json.loads(capsys.readouterr().out)
    assert result == publisher.manifest(source)
    assert "passed" not in result


@pytest.mark.parametrize("body", [b"", b"reviewed README\n", b"\xff\x00\x01"])
def test_blob_identifier_matches_git(body):
    result = subprocess.run(
        ["git", "hash-object", "--stdin"], input=body, capture_output=True, check=True
    )
    assert publisher.blob_sha(body) == result.stdout.decode().strip()

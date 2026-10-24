"""Public Pages provisioning is scoped to the attested repository and head."""

import copy
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/skills/mcp-builder/scripts"
)
sys.path.insert(0, str(SCRIPTS))
publisher = importlib.import_module("github_publish")
pages = importlib.import_module("github_pages")

REPOSITORY = "Example/connector"
REPOSITORY_ID = 1234
HEAD = "a" * 40
SEED = "b" * 40
BASE = f"repos/{REPOSITORY}"
SITE = {
    "build_type": "workflow",
    "public": True,
    "html_url": "https://example.github.io/connector/",
}
ABSENT = object()


class PagesAPI:
    """Reject every endpoint outside repository reads, Pages, and dispatch."""

    def __init__(self, site=ABSENT, *, branch="main"):
        self.site = copy.deepcopy(site) if site is not ABSENT else ABSENT
        self.branch = branch
        self.repository = {
            "id": REPOSITORY_ID,
            "full_name": REPOSITORY,
            "private": False,
            "is_template": False,
            "default_branch": branch,
        }
        self.workflow = {
            "id": 73,
            "path": ".github/workflows/pages.yml",
            "state": "active",
        }
        self.recheck_changes = {}
        self.recheck_after = 2
        self.head = HEAD
        self.recheck_head = HEAD
        self.repository_reads = 0
        self.pages_reads = 0
        self.calls = []
        self.fail_at = None

    @property
    def writes(self):
        return [
            (route, method, data)
            for route, method, data, _ in self.calls
            if method != "GET"
        ]

    def __call__(self, route, method="GET", data=None, *, allow_not_found=False):
        self.calls.append((route, method, copy.deepcopy(data), allow_not_found))
        if self.fail_at == (route, method):
            raise RuntimeError("Uncertain provider outcome")
        if route == BASE and method == "GET":
            self.repository_reads += 1
            changes = (
                self.recheck_changes
                if self.repository_reads >= self.recheck_after
                else {}
            )
            return copy.deepcopy(self.repository | changes)
        if (
            route == f"{BASE}/git/ref/heads/{quote(self.branch, safe='')}"
            and method == "GET"
        ):
            sha = (
                self.recheck_head
                if self.repository_reads >= self.recheck_after
                else self.head
            )
            return {"object": {"sha": sha}}
        if route == f"{BASE}/actions/workflows/pages.yml" and method == "GET":
            if self.workflow is None:
                raise RuntimeError("Workflow is absent")
            return copy.deepcopy(self.workflow)
        if route == f"{BASE}/pages" and method == "GET":
            self.pages_reads += 1
            assert allow_not_found is (self.pages_reads == 1)
            return None if self.site is ABSENT else copy.deepcopy(self.site)
        if route == f"{BASE}/pages" and method == "POST":
            assert self.site is ABSENT
            assert data["build_type"] == "workflow"
            self.site = copy.deepcopy(SITE)
            return copy.deepcopy(self.site)
        if (
            route == f"{BASE}/actions/workflows/pages.yml/dispatches"
            and method == "POST"
        ):
            assert data == {"ref": self.branch}
            return {}
        pytest.fail(f"Unexpected API operation: {method} {route}")


def provision(remote):
    return pages.provision(remote, REPOSITORY, REPOSITORY_ID, remote.branch, HEAD)


def test_absent_pages_created_once_then_dispatches_rechecked_branch():
    remote = PagesAPI(branch="release/docs")
    result = provision(remote)
    assert result == {
        "repository": REPOSITORY,
        "head": HEAD,
        "url": SITE["html_url"],
        "configured": True,
        "dispatch_requested": True,
        "deployment_verified": False,
    }
    assert remote.writes == [
        (f"{BASE}/pages", "POST", {"build_type": "workflow"}),
        (
            f"{BASE}/actions/workflows/pages.yml/dispatches",
            "POST",
            {"ref": "release/docs"},
        ),
    ]
    assert remote.repository_reads >= 2
    dispatch = next(
        i for i, call in enumerate(remote.calls) if call[0].endswith("/dispatches")
    )
    creation = next(
        i
        for i, call in enumerate(remote.calls)
        if call[:2] == (f"{BASE}/pages", "POST")
    )
    assert any(
        call[:2] == (BASE, "GET") for call in remote.calls[creation + 1 : dispatch]
    )
    assert any(
        "/git/ref/heads/" in call[0] for call in remote.calls[creation + 1 : dispatch]
    )


def test_existing_custom_domain_is_preserved_without_pages_mutation():
    custom = SITE | {
        "html_url": "https://docs.example.org/",
        "cname": "docs.example.org",
        "https_enforced": True,
    }
    remote = PagesAPI(custom)
    result = provision(remote)
    assert result["url"] == custom["html_url"]
    assert remote.site == custom
    assert remote.writes == [
        (f"{BASE}/actions/workflows/pages.yml/dispatches", "POST", {"ref": "main"})
    ]
    assert remote.repository_reads >= 2
    assert not result["deployment_verified"]


@pytest.mark.parametrize(
    "changes",
    [
        {"id": 5678},
        {"full_name": "Other/connector"},
        {"private": True},
        {"private": None},
        {"is_template": True},
        {"is_template": None},
        {"default_branch": "other"},
    ],
)
@pytest.mark.parametrize("phase", ["initial", "before_creation", "before_dispatch"])
def test_repository_drift_never_dispatches_or_changes_visibility(changes, phase):
    remote = PagesAPI()
    if phase == "initial":
        remote.repository.update(changes)
    else:
        remote.recheck_changes = changes
        remote.recheck_after = 3 if phase == "before_dispatch" else 2
    with pytest.raises((ValueError, RuntimeError, PermissionError)):
        provision(remote)
    assert not any(route.endswith("/dispatches") for route, _, _ in remote.writes)
    assert all(
        route == f"{BASE}/pages" and method == "POST"
        for route, method, _ in remote.writes
    )
    assert remote.writes == (
        [(f"{BASE}/pages", "POST", {"build_type": "workflow"})]
        if phase == "before_dispatch"
        else []
    )


@pytest.mark.parametrize("phase", ["initial", "before_creation", "before_dispatch"])
def test_head_drift_never_dispatches(phase):
    remote = PagesAPI()
    if phase == "initial":
        remote.head = "c" * 40
    else:
        remote.recheck_head = "c" * 40
        remote.recheck_after = 3 if phase == "before_dispatch" else 2
    with pytest.raises((ValueError, RuntimeError)):
        provision(remote)
    assert not any(route.endswith("/dispatches") for route, _, _ in remote.writes)
    assert remote.writes == (
        [(f"{BASE}/pages", "POST", {"build_type": "workflow"})]
        if phase == "before_dispatch"
        else []
    )


def test_existing_pages_repository_drift_prevents_dispatch_without_mutation():
    remote = PagesAPI(SITE)
    remote.recheck_changes = {"private": True}
    with pytest.raises(RuntimeError):
        provision(remote)
    assert remote.writes == []


@pytest.mark.parametrize(
    "arguments",
    [
        ("Example/connector/extra", REPOSITORY_ID, "main", HEAD),
        (REPOSITORY, 0, "main", HEAD),
        (REPOSITORY, True, "main", HEAD),
        (REPOSITORY, REPOSITORY_ID, "", HEAD),
        (REPOSITORY, REPOSITORY_ID, "main", ""),
    ],
)
def test_explicit_identity_branch_and_head_required_before_api(arguments):
    remote = PagesAPI()
    with pytest.raises(ValueError):
        pages.provision(remote, *arguments)
    assert remote.calls == []


@pytest.mark.parametrize("readback", [{}, SITE | {"public": False}])
def test_new_pages_readback_must_be_verified_before_dispatch(readback):
    remote = PagesAPI()

    def api(route, method="GET", data=None, **kwargs):
        result = remote(route, method, data, **kwargs)
        if route == f"{BASE}/pages" and method == "POST":
            remote.site = copy.deepcopy(readback)
        return result

    with pytest.raises(RuntimeError):
        pages.provision(api, REPOSITORY, REPOSITORY_ID, "main", HEAD)
    assert remote.writes == [(f"{BASE}/pages", "POST", {"build_type": "workflow"})]


@pytest.mark.parametrize(
    "site",
    [
        {},
        [],
        SITE | {"build_type": "legacy"},
        SITE | {"public": False},
        SITE | {"public": None},
        SITE | {"html_url": None},
        SITE | {"html_url": "http://example.github.io/connector/"},
        SITE | {"html_url": "https:///missing-host"},
        SITE | {"html_url": "javascript:alert(1)"},
    ],
)
def test_existing_incompatible_or_malformed_pages_is_preserved(site):
    remote = PagesAPI(site)
    with pytest.raises((ValueError, RuntimeError)):
        provision(remote)
    assert remote.site == site
    assert remote.writes == []


@pytest.mark.parametrize(
    "workflow", [None, {}, {"state": "disabled_manually"}, {"state": "deleted"}]
)
def test_missing_or_inactive_workflow_prevents_any_pages_mutation(workflow):
    remote = PagesAPI()
    remote.workflow = workflow
    with pytest.raises((ValueError, RuntimeError)):
        provision(remote)
    assert remote.writes == []


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/pages"),
        ("POST", "/pages"),
        ("POST", "/actions/workflows/pages.yml/dispatches"),
    ],
)
def test_provider_errors_and_uncertain_writes_are_not_retried(method, path):
    remote = PagesAPI()
    remote.fail_at = (BASE + path, method)
    with pytest.raises(RuntimeError):
        provision(remote)
    assert sum(call[:2] == remote.fail_at for call in remote.calls) == 1
    if path == "/pages":
        assert not any(route.endswith("/dispatches") for route, _, _ in remote.writes)
    assert all(method == "POST" for _, method, _ in remote.writes)


@pytest.fixture
def public_source(tmp_path):
    for name, content in {
        "README.md": "Reviewed connector\n",
        ".github/workflows/pages.yml": "name: Pages\non: workflow_dispatch\n",
        "mkdocs.yml": "site_name: Connector\n",
        "docs/index.md": "# Connector\n",
    }.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return tmp_path


class PublicationAPI(PagesAPI):
    """Minimal Git-tree readback, with all unexpected mutations rejected."""

    def __init__(self, *, public, corrupt_tree=False):
        super().__init__()
        self.repository["private"] = not public
        self.public = public
        self.head = self.recheck_head = SEED
        self.tree = []
        self.corrupt_tree = corrupt_tree
        self.tree_verified = False

    def __call__(self, route, method="GET", data=None, **kwargs):
        if method == "GET" and route in {BASE, f"{BASE}/git/ref/heads/main"}:
            return super().__call__(route, method, data, **kwargs)
        self.calls.append(
            (route, method, copy.deepcopy(data), kwargs.get("allow_not_found", False))
        )
        if route == "orgs/Example/repos" and method == "POST":
            assert data == {
                "name": "connector",
                "private": not self.public,
                "is_template": False,
                "auto_init": False,
            }
            return copy.deepcopy(self.repository)
        if route == f"{BASE}/contents/README.md" and method == "PUT":
            return {"commit": {"sha": SEED, "parents": []}}
        if route == f"{BASE}/git/trees" and method == "POST":
            self.tree = [
                {
                    "path": x["path"],
                    "mode": x["mode"],
                    "type": "blob",
                    "sha": publisher.blob_sha(x["content"].encode()),
                }
                for x in data["tree"]
            ]
            return {"sha": "d" * 40}
        if route == f"{BASE}/git/commits" and method == "POST":
            assert data["parents"] == [SEED]
            return {"sha": HEAD}
        if route == f"{BASE}/git/commits/{HEAD}" and method == "GET":
            return {"tree": {"sha": "d" * 40}}
        if route == f"{BASE}/git/trees/{'d' * 40}?recursive=1" and method == "GET":
            self.tree_verified = not self.corrupt_tree
            return {
                "tree": self.tree[:-1] if self.corrupt_tree else self.tree,
                "truncated": False,
            }
        if route == f"{BASE}/git/refs/heads/main" and method == "PATCH":
            assert self.tree_verified and data == {"sha": HEAD, "force": False}
            self.head = self.recheck_head = HEAD
            return {}
        pytest.fail(f"Unexpected publication API operation: {method} {route}")


@pytest.mark.parametrize("visibility", [None, "private", "public"])
def test_publication_defaults_private_and_only_public_provisions_attested_tree(
    public_source, monkeypatch, visibility
):
    remote = PublicationAPI(public=visibility == "public")
    monkeypatch.setattr(publisher, "api", remote)
    monkeypatch.setattr(publisher, "preflight", lambda *args: "orgs/Example/repos")
    calls = []

    def provision_spy(api, repository, repository_id, branch, expected_head):
        assert remote.tree_verified and remote.head == HEAD
        assert api is remote
        assert (repository, repository_id, branch, expected_head) == (
            REPOSITORY,
            REPOSITORY_ID,
            "main",
            HEAD,
        )
        calls.append(repository)
        return {
            "configured": True,
            "dispatch_requested": True,
            "deployment_verified": False,
        }

    monkeypatch.setattr(publisher, "provision", provision_spy)
    checks = {"passed": True, "files": publisher.manifest(public_source)}
    kwargs = {} if visibility is None else {"visibility": visibility}
    result = publisher.publish(
        public_source, "Example", "connector", checks, "Operator", **kwargs
    )
    expected = {
        "repository": REPOSITORY,
        "sha": HEAD,
        "private": visibility != "public",
        "files": checks["files"],
    }
    if visibility == "public":
        expected["pages"] = {
            "configured": True,
            "dispatch_requested": True,
            "deployment_verified": False,
        }
    assert result == expected
    assert calls == ([REPOSITORY] if visibility == "public" else [])


@pytest.mark.parametrize(
    "missing", [".github/workflows/pages.yml", "mkdocs.yml", "docs/index.md"]
)
def test_publication_requires_checked_docs_assets_before_remote_calls(
    public_source, monkeypatch, missing
):
    (public_source / missing).unlink()
    checks = {"passed": True, "files": publisher.manifest(public_source)}
    monkeypatch.setattr(
        publisher,
        "api",
        lambda *args, **kwargs: pytest.fail("Invalid public source reached API"),
    )
    monkeypatch.setattr(
        publisher,
        "preflight",
        lambda *args: pytest.fail("Invalid public source reached preflight"),
    )
    with pytest.raises(ValueError):
        publisher.publish(
            public_source,
            "Example",
            "connector",
            checks,
            "Operator",
            visibility="public",
        )


def test_failed_tree_attestation_never_calls_pages(public_source, monkeypatch):
    remote = PublicationAPI(public=True, corrupt_tree=True)
    monkeypatch.setattr(publisher, "api", remote)
    monkeypatch.setattr(publisher, "preflight", lambda *args: "orgs/Example/repos")
    monkeypatch.setattr(
        publisher,
        "provision",
        lambda *args: pytest.fail("Unattested tree reached Pages"),
    )
    checks = {"passed": True, "files": publisher.manifest(public_source)}
    with pytest.raises(RuntimeError):
        publisher.publish(
            public_source,
            "Example",
            "connector",
            checks,
            "Operator",
            visibility="public",
        )
    assert not any(method == "PATCH" for _, method, _ in remote.writes)


def test_private_publication_does_not_require_pages_assets(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("Private connector\n")
    remote = PublicationAPI(public=False)
    monkeypatch.setattr(publisher, "api", remote)
    monkeypatch.setattr(publisher, "preflight", lambda *args: "orgs/Example/repos")
    monkeypatch.setattr(
        publisher,
        "provision",
        lambda *args: pytest.fail("Private publication reached Pages"),
    )
    checks = {"passed": True, "files": publisher.manifest(tmp_path)}
    result = publisher.publish(tmp_path, "Example", "connector", checks, "Operator")
    assert result["private"] is True
    assert "pages" not in result
    assert not any("/pages" in route for route, _, _, _ in remote.calls)


def test_public_publication_uses_shared_pages_helper_after_tree_readback(
    public_source, monkeypatch
):
    remote = PublicationAPI(public=True)

    def api(route, method="GET", data=None, **kwargs):
        if route in {
            f"{BASE}/pages",
            f"{BASE}/actions/workflows/pages.yml",
            f"{BASE}/actions/workflows/pages.yml/dispatches",
        }:
            assert remote.tree_verified and remote.head == HEAD
            return PagesAPI.__call__(remote, route, method, data, **kwargs)
        return remote(route, method, data, **kwargs)

    monkeypatch.setattr(publisher, "api", api)
    monkeypatch.setattr(publisher, "preflight", lambda *args: "orgs/Example/repos")
    checks = {"passed": True, "files": publisher.manifest(public_source)}
    result = publisher.publish(
        public_source,
        "Example",
        "connector",
        checks,
        "Operator",
        visibility="public",
    )
    assert result["pages"] == {
        "repository": REPOSITORY,
        "head": HEAD,
        "url": SITE["html_url"],
        "configured": True,
        "dispatch_requested": True,
        "deployment_verified": False,
    }
    assert remote.writes[-2:] == [
        (f"{BASE}/pages", "POST", {"build_type": "workflow"}),
        (f"{BASE}/actions/workflows/pages.yml/dispatches", "POST", {"ref": "main"}),
    ]


@pytest.mark.parametrize("visibility", [None, "private", "public", "internal"])
def test_publication_cli_visibility_default_and_explicit_choice(
    tmp_path, monkeypatch, capsys, visibility
):
    checks = {"passed": True, "files": {}}
    checks_path = tmp_path / "checks.json"
    checks_path.write_text(json.dumps(checks))
    arguments = [
        "github_publish.py",
        "publish",
        str(tmp_path),
        "--owner",
        "Example",
        "--name",
        "connector",
        "--expected-login",
        "Operator",
        "--checks",
        str(checks_path),
    ]
    if visibility is not None:
        arguments.extend(["--visibility", visibility])
    calls = []

    def publish(*args, **kwargs):
        calls.append((args, kwargs))
        return {"private": kwargs["visibility"] == "private"}

    monkeypatch.setattr(sys, "argv", arguments)
    monkeypatch.setattr(publisher, "publish", publish)
    monkeypatch.setattr(
        publisher,
        "api",
        lambda *args, **kwargs: pytest.fail("CLI unexpectedly reached API"),
    )
    if visibility == "internal":
        with pytest.raises(SystemExit) as error:
            publisher.main()
        assert error.value.code == 2
        assert calls == []
    else:
        publisher.main()
        expected = visibility or "private"
        assert calls == [
            (
                (tmp_path, "Example", "connector", checks, "Operator"),
                {"visibility": expected},
            )
        ]
        assert json.loads(capsys.readouterr().out) == {"private": expected == "private"}


@pytest.mark.parametrize("status", [403, 404, 409, 500])
@pytest.mark.parametrize("allow_not_found", [False, True])
def test_api_only_explicit_404_is_an_allowed_absence(
    monkeypatch, status, allow_not_found
):
    seen = []

    def run(command, **kwargs):
        seen.append(command)
        return SimpleNamespace(
            returncode=1, stdout="", stderr=f"gh: request failed (HTTP {status})"
        )

    monkeypatch.setattr(publisher.subprocess, "run", run)
    if status == 404 and allow_not_found:
        assert publisher.api(f"{BASE}/pages", allow_not_found=True) is None
    else:
        with pytest.raises(RuntimeError):
            publisher.api(f"{BASE}/pages", allow_not_found=allow_not_found)
    assert len(seen) == 1


def test_failed_write_404_is_not_allowed_absence_or_retried(monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=1, stdout="", stderr="HTTP 404")

    monkeypatch.setattr(publisher.subprocess, "run", run)
    with pytest.raises(RuntimeError):
        publisher.api(
            f"{BASE}/pages", "POST", {"build_type": "workflow"}, allow_not_found=True
        )
    assert len(calls) == 1


def test_empty_successful_204_dispatch_response_is_accepted(monkeypatch):
    monkeypatch.setattr(
        publisher.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    assert (
        publisher.api(
            f"{BASE}/actions/workflows/pages.yml/dispatches", "POST", {"ref": "main"}
        )
        == {}
    )


@pytest.mark.parametrize("actor", ["Operator", "Other"])
def test_standalone_pages_command_binds_actor_repository_id_and_head(
    monkeypatch, capsys, actor
):
    remote = PagesAPI(SITE, branch="release/docs")
    calls = []

    def api(route, *args, **kwargs):
        if route == "user":
            return {"login": actor}
        return remote(route, *args, **kwargs)

    def provision_spy(api, repository, repository_id, branch, expected_head):
        calls.append((repository, repository_id, branch, expected_head))
        return {"url": SITE["html_url"], "deployment_verified": False}

    monkeypatch.setattr(publisher, "api", api)
    monkeypatch.setattr(publisher, "provision", provision_spy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "github_publish.py",
            "pages",
            "--owner",
            "Example",
            "--name",
            "connector",
            "--expected-login",
            "Operator",
            "--repository-id",
            str(REPOSITORY_ID),
            "--expected-head",
            HEAD,
        ],
    )
    if actor == "Other":
        with pytest.raises(PermissionError):
            publisher.main()
        assert calls == []
    else:
        publisher.main()
        assert calls == [(REPOSITORY, REPOSITORY_ID, "release/docs", HEAD)]
        assert json.loads(capsys.readouterr().out)["deployment_verified"] is False
    assert remote.writes == []

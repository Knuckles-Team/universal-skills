"""Golden-file tests for the requests -> SDK governed client codemod (sdk_centralize.py)."""

import filecmp
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
import sdk_centralize  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures/sdk_centralize"
AUTO = ["caddy-mcp", "lgtm-mcp", "mattermost-mcp"]
EXCEPTIONS = {"ciso-assistant-api": "retry-loop", "owncast-agent": "catches-requests-errors"}


def _tree(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def _materialize(src: Path, dest: Path) -> None:
    """Copy a fixture tree, restoring ``*.py.fixture`` to ``*.py`` (hooks and pytest never see fixture code)."""
    for p in src.rglob("*"):
        if p.is_file():
            out = dest / p.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            out = out.with_name(out.name.removesuffix(".fixture"))
            out.write_bytes(p.read_bytes())


@pytest.mark.parametrize("name", AUTO)
def test_auto_matches_golden_after_tree(name, tmp_path):
    work = tmp_path / name
    _materialize(FIXTURES / name / "before", work)
    result = sdk_centralize.run(work, apply=True, sdk_version="0.3.12")
    assert result.verdict == "AUTO"
    golden = tmp_path / "golden"
    _materialize(FIXTURES / name / "after", golden)
    assert _tree(work) == _tree(golden)


@pytest.mark.parametrize("name", AUTO)
def test_dry_run_writes_nothing_and_apply_is_idempotent(name, tmp_path):
    work = tmp_path / name
    _materialize(FIXTURES / name / "before", work)
    before = _tree(work)
    dry = sdk_centralize.run(work, apply=False, sdk_version="0.3.12")
    assert dry.verdict == "AUTO" and _tree(work) == before
    sdk_centralize.run(work, apply=True, sdk_version="0.3.12")
    once = _tree(work)
    again = sdk_centralize.run(work, apply=True, sdk_version="0.3.12")
    assert again.applied == [] and _tree(work) == once


@pytest.mark.parametrize(("name", "code"), sorted(EXCEPTIONS.items()))
def test_exception_repos_are_classified_and_unchanged(name, code, tmp_path):
    work = tmp_path / name
    _materialize(FIXTURES / name / "before", work)
    before = _tree(work)
    result = sdk_centralize.run(work, apply=True, sdk_version="0.3.12")
    assert result.verdict == "EXCEPTION"
    assert any(r.startswith(code) for r in result.reasons)
    assert _tree(work) == before


def test_generated_client_has_governed_shape(tmp_path):
    work = tmp_path / "x"
    _materialize(FIXTURES / "lgtm-mcp" / "before", work)
    sdk_centralize.run(work, apply=True, sdk_version="0.3.12")
    text = (work / "lgtm_mcp/api/api_client_base.py").read_text()
    assert "requests" not in text and "create_http_client" in text and "BearerAuth(token)" in text
    spec = (work / "specs/sdk-centralization/requirements.md").read_text()
    assert "CONN-LGTM-MCP-SDK-CENTRALIZATION-R001" in spec and "SDK-CENTRALIZED-CAPABILITIES-R001" in spec
    assert not filecmp.cmp(work / "pyproject.toml", FIXTURES / "lgtm-mcp/before/pyproject.toml", shallow=False)


def test_bump_skips_already_tagged_versions(tmp_path):
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    (repo / ".bumpversion.cfg").write_text(
        '[bumpversion]\ncurrent_version = 1.2.3\n\n[bumpversion:file:pyproject.toml]\nsearch = version = "{current_version}"\nreplace = version = "{new_version}"\n'
        '\n[bumpversion:file(docker-img):docker/Dockerfile]\nsearch = =={current_version}"\nreplace = =={new_version}"\n'
    )
    (repo / "pyproject.toml").write_text('version = "1.2.3"\n')
    (repo / "docker").mkdir()
    (repo / "docker/Dockerfile").write_text('RUN pip install "pkg==1.2.3"\n')
    for cmd in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], ["tag", "v1.2.4"]):
        subprocess.run(["git", "-C", str(repo), *cmd], check=True)
    res = sdk_centralize.Result("r")
    sdk_centralize.bump_patch(repo, res, apply=True)
    assert 'version = "1.2.5"' in (repo / "pyproject.toml").read_text()
    assert '==1.2.5"' in (repo / "docker/Dockerfile").read_text()

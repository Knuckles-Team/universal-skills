"""Build a generated site and exercise the shared Pages delivery contract offline."""

from __future__ import annotations

import ast
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
from urllib.parse import unquote, urlsplit

import pytest
import yaml


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "universal_skills/agent-tools/mcp-builder/scripts"
)
SPEC_FILES = {
    "spec.md",
    "plan.md",
    "requirements.md",
    "tasks.md",
    "test-spec.md",
    "status.json",
}


def _run(command: list[str], root: Path, *, env: dict[str, str] | None = None) -> str:
    if command[0] == "git":
        env = dict(os.environ if env is None else env)
        # Git hooks export repository-local variables; foreign fixture repos must
        # not inherit the outer worktree's index, object directory or work tree.
        names = subprocess.check_output(
            ["git", "rev-parse", "--local-env-vars"], text=True
        ).splitlines()
        for name in names:
            env.pop(name, None)
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def test_fixture_git_commands_preserve_the_calling_repository(tmp_path, monkeypatch):
    parent = tmp_path / "parent"
    foreign = tmp_path / "fixture"
    parent.mkdir()
    foreign.mkdir()
    _run(["git", "init", "-q"], parent)
    (parent / "sentinel.txt").write_text("parent content\n")
    _run(["git", "add", "."], parent)
    commit = [
        "git",
        "-c",
        "user.name=Codex",
        "-c",
        "user.email=noreply@openai.com",
        "commit",
        "-qm",
        "Isolated fixture",
    ]
    _run(commit, parent)
    before = (
        _run(["git", "rev-parse", "HEAD"], parent),
        _run(["git", "write-tree"], parent),
    )
    monkeypatch.setenv("GIT_DIR", str(parent / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(parent))
    monkeypatch.setenv("GIT_INDEX_FILE", str(parent / ".git/index"))
    _run(["git", "init", "-q"], foreign)
    (foreign / "fixture.txt").write_text("fixture content\n")
    _run(["git", "add", "."], foreign)
    _run(commit, foreign)
    assert _run(["git", "ls-files"], foreign).splitlines() == ["fixture.txt"]
    assert (
        _run(["git", "rev-parse", "HEAD"], parent),
        _run(["git", "write-tree"], parent),
    ) == before


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    parent = tmp_path_factory.mktemp("generated-site")
    _run(
        [
            sys.executable,
            str(SCRIPTS / "scaffold_package.py"),
            "site-contract",
            "--output-dir",
            str(parent),
        ],
        parent,
    )
    return parent / "site-contract"


def _capability(root: Path) -> tuple[Path, dict]:
    candidates = [
        path
        for path in (root / "specs").glob("*/status.json")
        if path.parent.name != "_template"
    ]
    assert len(candidates) == 1, (
        "a generated connector needs one starter capability spec"
    )
    path = candidates[0]
    return path.parent, json.loads(path.read_text())




OFFLINE_DASHBOARD = textwrap.dedent("""\
    import json
    from pathlib import Path
    import socket
    import sys
    import urllib.request

    def offline(*args, **kwargs):
        raise OSError("network disabled in generated-site acceptance")

    socket.socket.connect = offline
    urllib.request.urlopen = offline
    sys.path.insert(0, sys.argv[1])
    from spec_dashboard import main
    from spec_graph_load import load_repo

    root = Path(sys.argv[2]).resolve()
    assert main(['--root', str(root), '--config', '.config/spec-dashboard.json',
                 '--repository', 'Knuckles-Team/site-contract',
                 '--output', 'site/spec-delivery']) == 0
    requirements = load_repo(root)
    assert requirements
    for identifier, requirement in requirements.items():
        assert requirement.requirement_text, identifier
        assert requirement.verification_text, identifier
        assert requirement.delivery_state == 'SPECIFIED'
        assert requirement.depends_on <= requirements.keys()
    print(json.dumps({'requirements': len(requirements),
                      'dependencies': {key: sorted(row.depends_on)
                                       for key, row in requirements.items()}}))
    """)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(
                value for name, value in attrs if name == "href" and value
            )


def _links(path: Path) -> list[str]:
    parsed = Links()
    parsed.feed(path.read_text())
    return parsed.hrefs

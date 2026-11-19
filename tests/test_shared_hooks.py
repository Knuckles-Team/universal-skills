"""US-CONTENT-R001.7 and US-CONTENT-R001.8: shared hooks replace the repository's own sanitizer and spelling hooks."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], check=True, capture_output=True, text=True)
    return [name for name in out.stdout.split("\0") if name]


@pytest.mark.spec("US-CONTENT-R001.7")
def test_shared_hooks_replace_the_local_sanitizer_and_codespell() -> None:
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    shared = {h["id"] for repo in config["repos"] if repo["repo"].endswith("/pipelines") for h in repo["hooks"]}
    assert {"secrets", "connector-standard"} <= shared
    ids = {h["id"] for repo in config["repos"] for h in repo["hooks"]}
    assert "security-sanitizer" not in ids and "codespell" not in ids
    tracked = set(_tracked())
    assert not {"scripts/security_sanitizer.py", ".codespellignore"} & tracked
    assert not [name for name in tracked if name.endswith(".skill")]
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    for job in ("gates", "gates-all-files"):
        setup = workflow["jobs"][job]["with"]["setup-command"]
        assert "PROHIBITED_IDENTITY_CATALOG" in setup and "prohibited-identities.json" in setup, job


@pytest.mark.spec("US-CONTENT-R001.8")
def test_every_accepted_spelling_word_occurs_in_tracked_text() -> None:
    table = PYPROJECT["tool"]["pipelines"]["codespell"]
    skip = [*table["exclude"], *PYPROJECT["tool"]["pipelines"]["connector"]["vendored"]]
    text = ""
    for name in _tracked():
        path = ROOT / name
        if path.suffix in {".md", ".py", ".txt", ".toml", ".yaml", ".yml", ".json", ".sh"} and not any(
            name == s or name.startswith(s + "/") for s in skip
        ):
            text += "\n" + path.read_text(encoding="utf-8", errors="ignore")
    unused = [w for w in table["ignore_words"] if not re.search(rf"(?<![A-Za-z]){re.escape(w)}(?![A-Za-z])", text, re.I)]
    assert not unused, unused

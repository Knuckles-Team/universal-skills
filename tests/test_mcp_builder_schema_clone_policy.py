"""The optional shared wrapper cannot hide handwritten or modified scan inputs."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).parents[1]
    / "universal_skills/skills/mcp-builder/scripts/templates/generated_schema_clones.py"
)


@pytest.fixture
def wrapper(tmp_path, monkeypatch):
    verifier = ModuleType("verify_generated_schemas")
    verifier.MANIFEST = "policy.json"
    verifier.load_policy = lambda root: json.loads((root / "policy.json").read_text())
    monkeypatch.setitem(sys.modules, verifier.__name__, verifier)
    spec = importlib.util.spec_from_file_location("clones_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_only_both_verified_members_are_filtered(wrapper):
    keys = [
        ("json", "digest", paths, 0)
        for paths in (
            ("generated.json", "generated.json"),
            ("handwritten.py", "generated.json"),
            ("a.py", "b.py"),
        )
    ]
    pairs = dict.fromkeys(keys, ())
    retained = wrapper.retain_pairs(pairs, {"generated.json": "hash"})
    assert set(retained) == set(keys[1:])
    assert wrapper.retain_pairs(pairs, {}) == pairs


@pytest.mark.parametrize("mutation", ["rewrite", "new", "mode"])
def test_verifier_cannot_change_any_scanned_file(
    wrapper, tmp_path, monkeypatch, mutation
):
    policy = {"artifacts": {"generated.json": "hash"}}
    (tmp_path / "policy.json").write_text(json.dumps(policy))
    source = tmp_path / "handwritten.py"
    source.write_text("original")
    source.chmod(0o644)

    def run(*args, **kwargs):
        if mutation == "rewrite":
            source.write_text("changed")
        elif mutation == "new":
            (tmp_path / "new.py").write_text("new")
        else:
            source.chmod(0o755)
        return subprocess.CompletedProcess(
            args,
            0,
            stdout=json.dumps(
                {"version": 1, "verified_artifacts": policy["artifacts"]}
            ),
        )

    monkeypatch.setattr(wrapper.subprocess, "run", run)
    with pytest.raises(ValueError, match="changed the scanned tree"):
        wrapper.verified_artifacts(tmp_path, tmp_path)


def test_absent_historical_policy_never_exempts(wrapper, tmp_path):
    assert wrapper.verified_artifacts(tmp_path, tmp_path) == {}


def test_special_scan_paths_fail_closed(wrapper, tmp_path):
    (tmp_path / "link").symlink_to(tmp_path / "outside")
    with pytest.raises(ValueError, match="link or special"):
        wrapper.tree_state(tmp_path)

"""US-CONTENT-R002: skills vendored from pinned upstream repositories."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "sync_upstream_skills", ROOT / "scripts" / "sync_upstream_skills.py"
)
assert _spec and _spec.loader
sus = importlib.util.module_from_spec(_spec)
sys.modules["sync_upstream_skills"] = sus
_spec.loader.exec_module(sus)

SHA = "0123456789abcdef0123456789abcdef01234567"
RETIRED = (
    "spec-generator",
    "task-planner",
    "spec-verifier",
    "spec-intake-wizard",
    "feature-development-pipeline",
)
SPECKIT = (
    "constitution",
    "specify",
    "clarify",
    "plan",
    "tasks",
    "analyze",
    "checklist",
    "implement",
)


def manifest(
    tmp: Path,
    commit: str = SHA,
    license_: str | None = "MIT",
    extra: str = "",
    repo: str = "https://example.invalid/x",
    skill_path: str = "cmds/one.md",
) -> Path:
    lic = f'license = "{license_}"\nlicense_path = "LICENSE"\n' if license_ else ""
    path = tmp / "upstream-sources.toml"
    path.write_text(
        "# keep this comment\n"
        "[[source]]\n"
        'id = "demo"\n'
        f'repository = "{repo}"\n'
        'track = "main"\n'
        f'commit = "{commit}"\n'
        f"{lic}"
        'transform = "command-md"\n'
        'paths = ["cmds/*.md"]\n'
        f"{extra}\n"
        "[[source.skill]]\n"
        'name = "demo-one"\n'
        f'path = "{skill_path}"\n'
        'trigger = "Use when demoing."\n',
        encoding="utf-8",
    )
    return path


COMMAND = (
    "---\n"
    "description: Do the thing.\n"
    "handoffs:\n  - label: Next\n    agent: speckit.next\n"
    "scripts:\n  sh: scripts/bash/do.sh --json\n  ps: scripts/powershell/do.ps1\n"
    "---\n\n"
    "Run `{SCRIPT}` then see __SPECKIT_COMMAND_NEXT__ with {ARGS}.\n"
)


def src_of(tmp: Path) -> object:
    return sus.load_manifest(manifest(tmp))[0]


@pytest.mark.spec("US-CONTENT-R002.1")
def test_manifest_rejects_incomplete_sources(tmp_path: Path) -> None:
    sources = sus.load_manifest(sus.MANIFEST)
    assert sources and all(s.skills and s.paths for s in sources)
    assert sus.load_manifest(manifest(tmp_path))[0].skills[0].name == "demo-one"
    with pytest.raises(sus.SyncError, match="matches no glob"):
        sus.load_manifest(manifest(tmp_path, skill_path="other/one.md"))
    broken = manifest(tmp_path).read_text().replace('transform = "command-md"\n', "")
    (tmp_path / "b.toml").write_text(broken)
    with pytest.raises(sus.SyncError, match="missing transform"):
        sus.load_manifest(tmp_path / "b.toml")
    dup = manifest(tmp_path).read_text() + (
        '\n[[source.skill]]\nname = "demo-one"\npath = "cmds/one.md"\n'
    )
    (tmp_path / "d.toml").write_text(dup)
    with pytest.raises(sus.SyncError, match="two sources"):
        sus.load_manifest(tmp_path / "d.toml")


@pytest.mark.spec("US-CONTENT-R002.2")
def test_pin_must_be_full_commit_sha(tmp_path: Path) -> None:
    for bad in ("main", "v1.0.12", SHA[:12], SHA.upper(), SHA + "0"):
        with pytest.raises(sus.SyncError, match="40-hex"):
            sus.load_manifest(manifest(tmp_path, commit=bad))
    assert sus.load_manifest(manifest(tmp_path))[0].commit == SHA
    for real in sus.load_manifest(sus.MANIFEST):
        assert re.fullmatch(r"[0-9a-f]{40}", real.commit)


@pytest.mark.spec("US-CONTENT-R002.3")
def test_license_is_required_and_kept(tmp_path: Path) -> None:
    with pytest.raises(sus.SyncError, match="missing license"):
        sus.load_manifest(manifest(tmp_path, license_=None))
    for src in sus.load_manifest(sus.MANIFEST):
        assert src.license
        snapshot = sus.read_snapshot(src)
        assert snapshot[src.license_path].strip()
        for sk in src.skills:
            folder = sus.SKILLS_DIR / sk.name
            assert (folder / "LICENSE").read_bytes() == snapshot[src.license_path]
            assert f"License: {src.license}" in (folder / "UPSTREAM.md").read_text()


@pytest.mark.spec("US-CONTENT-R002.4")
def test_transforms_are_deterministic(tmp_path: Path) -> None:
    src = src_of(tmp_path)
    sk = src.skills[0]
    first = sus.render_command(src, sk, COMMAND.encode(), "9.9.9")
    assert first == sus.render_command(src, sk, COMMAND.encode(), "9.9.9")
    text = first.decode()
    assert text.startswith("---\nname: demo-one\n")
    assert "version: '9.9.9'" in text
    assert "Do the thing. Use when demoing." in text
    assert ".specify/scripts/bash/do.sh --json" in text
    assert "speckit-next" in text and "$ARGUMENTS" in text
    assert "handoffs" not in text and "{SCRIPT}" not in text

    folder = {
        "pk/skill/SKILL.md": b"---\nname: s\nmetadata:\n  version: '0.0.1'\n---\nBody\n",
        "pk/skill/scripts/x.py": b"print(1)\n",
        "pk/other/SKILL.md": b"unrelated",
    }
    sk2 = sus.SkillDecl("s", "pk/skill")
    one = sus.render_skill_md(src, sk2, folder, "9.9.9")
    assert one == sus.render_skill_md(src, sk2, folder, "9.9.9")
    assert set(one) == {"SKILL.md", "scripts/x.py"}
    assert one["scripts/x.py"] == folder["pk/skill/scripts/x.py"]
    assert b"version: '9.9.9'" in one["SKILL.md"] and b"0.0.1" not in one["SKILL.md"]
    assert one["SKILL.md"].endswith(b"Body\n")


def overlay(folder: Path, name: str, header: str, body: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(f"---\n{header}\n---\n{body}\n", encoding="utf-8")


@pytest.mark.spec("US-CONTENT-R002.5")
def test_overlay_merge_is_ordered_and_strict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sus, "OVERLAYS_DIR", tmp_path)
    folder = tmp_path / "demo-one"
    overlay(folder, "20-append.md", "mode: append", "TAIL TWO")
    overlay(folder, "10-append.md", "mode: append", "TAIL ONE")
    overlay(folder, "30-replace.md", "mode: replace\nmatch: old line", "new line")
    overlay(folder, "40-after.md", "mode: insert-after\nmatch: anchor", "inserted")
    overlay(folder, "50-prepend.md", "mode: prepend", "HEAD")
    overlay(folder, "60-file.md", "mode: file\ndest: references/r.md", "ref body")
    base = "---\nname: demo-one\n---\n\n# demo-one\n\nold line\nanchor\nend\n"

    def merge() -> tuple[str, dict[str, bytes]]:
        extra: dict[str, bytes] = {}
        return sus.apply_overlays(base, sus.load_overlays("demo-one"), extra), extra

    merged, extra = merge()
    assert merged == merge()[0]
    assert merged.index("TAIL ONE") < merged.index("TAIL TWO")
    assert "new line" in merged and "old line" not in merged
    assert "anchor\ninserted\nend" in merged
    assert merged.index("# demo-one") < merged.index("HEAD") < merged.index("new line")
    assert extra == {"references/r.md": b"ref body\n"}
    overlay(folder, "70-bad.md", "mode: replace\nmatch: nowhere", "x")
    with pytest.raises(sus.SyncError, match="exactly one line"):
        merge()
    (folder / "70-bad.md").write_text("no header\n")
    with pytest.raises(sus.SyncError, match="header"):
        sus.load_overlays("demo-one")


def make_upstream(tmp: Path, description: str = "Do the thing.") -> tuple[Path, str]:
    repo = tmp / "up"
    (repo / "cmds").mkdir(parents=True)
    (repo / "cmds" / "one.md").write_text(COMMAND.replace("Do the thing.", description))
    (repo / "LICENSE").write_text("MIT License\n\nCopyright Example\n")
    marker = tmp / "RAN"
    (repo / "run.sh").write_text(f"#!/bin/sh\ntouch {marker}\n")
    (repo / "run.sh").chmod(0o755)
    hooks = repo / ".git" / "hooks"

    def git(*a: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
             "-c", "commit.gpgsign=false", *a],
            cwd=repo, check=True, capture_output=True, text=True,
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    hooks.mkdir(exist_ok=True)
    (hooks / "post-commit").write_text(f"#!/bin/sh\ntouch {marker}\n")
    (hooks / "post-commit").chmod(0o755)
    git("add", "--", "cmds/one.md", "LICENSE", "run.sh")
    git("commit", "-q", "-m", "one")
    return repo, git("rev-parse", "HEAD")


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    for attr, name in (("SKILLS_DIR", "skills"), ("SNAPSHOT_DIR", "upstream"),
                       ("OVERLAYS_DIR", "overlays")):
        monkeypatch.setattr(sus, attr, tmp_path / name)
    (tmp_path / "skills").mkdir()
    repo, sha = make_upstream(tmp_path)
    mpath = tmp_path / "upstream-sources.toml"
    monkeypatch.setattr(sus, "MANIFEST", mpath)
    manifest(tmp_path, commit=sha, repo=str(repo))
    marker = tmp_path / "RAN"
    marker.unlink(missing_ok=True)
    return {"tmp": tmp_path, "repo": repo, "sha": sha, "marker": marker}


@pytest.mark.spec("US-CONTENT-R002.6")
def test_sync_writes_provenance_without_running_code(world: dict) -> None:
    src = sus.load_manifest()[0]
    sus.sync_source(src, "1.2.3", today="2026-01-02")
    skill = sus.SKILLS_DIR / "demo-one"
    prov = (skill / "UPSTREAM.md").read_text()
    for needle in (
        f"Source: {world['repo']}",
        f"`{world['sha']}`",
        "`cmds/one.md`",
        "License: MIT",
        "Synced: 2026-01-02",
        "Source digest: sha256:",
        "Local overlays:",
    ):
        assert needle in prov, needle
    assert "Copyright Example" in (skill / "LICENSE").read_text()
    assert (sus.SNAPSHOT_DIR / "demo" / "cmds" / "one.md").is_file()
    assert not (sus.SNAPSHOT_DIR / "demo" / "run.sh").exists()
    assert not world["marker"].exists()
    assert sus.check_source(src, "1.2.3") == []


@pytest.mark.spec("US-CONTENT-R002.7")
def test_check_detects_hand_edits_and_overlay_drift(world: dict) -> None:
    src = sus.load_manifest()[0]
    sus.sync_source(src, "1.2.3", today="2026-01-02")
    skill = sus.SKILLS_DIR / "demo-one"
    assert sus.check_source(src, "1.2.3", verify_pin=True) == []
    assert sus.check_source(src, "1.2.4"), "a stale package version is drift"

    original = (skill / "SKILL.md").read_text()
    (skill / "SKILL.md").write_text(original + "hand edit\n")
    assert any("SKILL.md" in p for p in sus.check_source(src, "1.2.3"))
    (skill / "SKILL.md").write_text(original)
    (skill / "extra.md").write_text("x")
    assert any("extra.md" in p for p in sus.check_source(src, "1.2.3"))
    (skill / "extra.md").unlink()

    overlay(sus.OVERLAYS_DIR / "demo-one", "10-x.md", "mode: append", "LOCAL")
    assert any("SKILL.md" in p for p in sus.check_source(src, "1.2.3"))
    sus.sync_source(src, "1.2.3", today="2026-02-03")
    assert "LOCAL" in (skill / "SKILL.md").read_text()
    assert "10-x.md" in (skill / "UPSTREAM.md").read_text()
    assert sus.check_source(src, "1.2.3") == []

    snap = sus.SNAPSHOT_DIR / "demo" / "cmds" / "one.md"
    snap.write_text(snap.read_text() + "tamper\n")
    assert sus.check_source(src, "1.2.3", verify_pin=True)
    assert sus.main(["--check"]) == 1


@pytest.mark.spec("US-CONTENT-R002.8")
def test_update_moves_the_pin_and_resyncs(
    world: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = sus.load_manifest()[0]
    sus.sync_source(src, "1.2.3")
    repo = world["repo"]
    (repo / "cmds" / "one.md").write_text(COMMAND.replace("Do the thing.", "Do it better."))
    env = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
           "-c", "commit.gpgsign=false"]
    subprocess.run([*env, "commit", "-q", "-am", "two"], cwd=repo, check=True)
    new = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                         capture_output=True, text=True).stdout.strip()
    assert new != world["sha"]
    monkeypatch.setattr(sus, "package_version", lambda: "1.2.3")
    assert sus.main(["--update", "demo"]) == 0
    text = sus.MANIFEST.read_text()
    assert f'commit = "{new}"' in text and "# keep this comment" in text
    assert "Do it better." in (sus.SKILLS_DIR / "demo-one" / "SKILL.md").read_text()
    assert sus.main(["--check", "--verify-pin"]) == 0
    assert sus.main(["--update", "missing"]) == 2


@pytest.mark.spec("US-CONTENT-R002.9")
def test_spec_kit_skills_replace_the_retired_skills() -> None:
    sources = {s.id: s for s in sus.load_manifest(sus.MANIFEST)}
    kit = sources["spec-kit"]
    assert {sk.name for sk in kit.skills} == {f"speckit-{c}" for c in SPECKIT}
    assert sus.check_source(kit, sus.package_version()) == []
    for sk in kit.skills:
        folder = sus.SKILLS_DIR / sk.name
        assert (folder / "UPSTREAM.md").is_file() and (folder / "LICENSE").is_file()
        assert sus.load_overlays(sk.name), f"{sk.name} carries no repository extensions"
    for name in RETIRED:
        assert not (sus.SKILLS_DIR / name).exists(), name
    pattern = re.compile("|".join(map(re.escape, RETIRED)))
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout.split("\n")
    skip = {"CHANGELOG.md", "uv.lock", "tests/test_upstream_sources.py"}
    for rel in filter(None, tracked):
        path = ROOT / rel
        if rel in skip or rel.startswith("specs/catalog-content/") or not path.is_file() or path.suffix in {".skill", ".png"}:
            continue
        try:
            hit = pattern.search(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        assert not hit, f"{rel} still refers to {hit.group(0) if hit else ''}"


@pytest.mark.spec("US-CONTENT-R002.10")
def test_hook_and_installer_are_wired() -> None:
    config = (ROOT / ".pre-commit-config.yaml").read_text()
    assert "scripts/sync_upstream_skills.py --check" in config
    skill = (ROOT / "universal_skills/skills/universal-installer/SKILL.md").read_text()
    for needle in ("--update", "--check --verify-pin", "pull request", "Never push to the default"):
        assert needle in skill, needle

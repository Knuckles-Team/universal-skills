#!/usr/bin/env python3
"""Vendor skills from pinned upstream repositories (US-CONTENT-R002).

The manifest ``upstream-sources.toml`` lists every source: repository URL, a full
commit SHA, path globs, the skills it produces, the license and a transform.
This script copies the pinned files into ``universal_skills/upstream/<id>/`` (the
pristine snapshot), renders each skill into ``universal_skills/skills/<name>/``
and merges the overlays from ``universal_skills/overlays/<name>/`` after it.
No upstream code is ever executed: files are read from the git object store only.

Usage:
    python scripts/sync_upstream_skills.py                  # sync every source at its pin
    python scripts/sync_upstream_skills.py --source ID      # sync one source
    python scripts/sync_upstream_skills.py --check          # offline drift check (hook)
    python scripts/sync_upstream_skills.py --check --verify-pin   # also compare to upstream
    python scripts/sync_upstream_skills.py --update ID      # bump the pin to the latest, re-sync
"""

from __future__ import annotations

import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PKG = REPO / "universal_skills"
MANIFEST = REPO / "upstream-sources.toml"
SKILLS_DIR = PKG / "skills"
OVERLAYS_DIR = PKG / "overlays"
SNAPSHOT_DIR = PKG / "upstream"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
TRANSFORMS = ("skill-md", "command-md")
OVERLAY_MODES = ("append", "prepend", "replace", "insert-after", "file")
PROVENANCE = "UPSTREAM.md"
LICENSE_FILE = "LICENSE"


class SyncError(Exception):
    """A manifest, fetch, overlay or drift error."""


@dataclass
class SkillDecl:
    name: str
    path: str
    trigger: str = ""


@dataclass
class Source:
    id: str
    repository: str
    commit: str
    track: str
    license: str
    license_path: str
    transform: str
    paths: list[str]
    skills: list[SkillDecl] = field(default_factory=list)
    script_prefix: str = ".specify/"


# ---------------------------------------------------------------- manifest


def load_manifest(path: Path | None = None) -> list[Source]:
    """Parse and validate the manifest; raise SyncError on any violation."""
    path = path or MANIFEST
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SyncError(f"cannot read manifest {path}: {exc}") from exc
    raw_sources = data.get("source")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise SyncError("manifest declares no [[source]]")
    sources: list[Source] = []
    seen_ids: set[str] = set()
    seen_skills: set[str] = set()
    for raw in raw_sources:
        sid = str(raw.get("id", ""))
        if not NAME_RE.match(sid):
            raise SyncError(f"source id {sid!r} must be kebab-case")
        if sid in seen_ids:
            raise SyncError(f"duplicate source id {sid}")
        seen_ids.add(sid)
        for key in ("repository", "commit", "license", "transform", "paths"):
            if not raw.get(key):
                raise SyncError(f"source {sid}: missing {key}")
        if not SHA_RE.match(raw["commit"]):
            raise SyncError(
                f"source {sid}: commit must be a full 40-hex SHA, never a branch or tag"
            )
        if raw["transform"] not in TRANSFORMS:
            raise SyncError(f"source {sid}: transform must be one of {TRANSFORMS}")
        if not raw.get("license_path"):
            raise SyncError(f"source {sid}: license_path is required (keep the license)")
        paths = raw["paths"]
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            raise SyncError(f"source {sid}: paths must be a list of globs")
        src = Source(
            id=sid,
            repository=raw["repository"],
            commit=raw["commit"],
            track=raw.get("track", "main"),
            license=raw["license"],
            license_path=raw["license_path"],
            transform=raw["transform"],
            paths=paths,
            script_prefix=raw.get("script_prefix", ".specify/"),
        )
        for sk in raw.get("skill", []):
            name = str(sk.get("name", ""))
            spath = str(sk.get("path", ""))
            if not NAME_RE.match(name):
                raise SyncError(f"source {sid}: skill name {name!r} must be kebab-case")
            if name in seen_skills:
                raise SyncError(f"skill {name} is produced by two sources")
            seen_skills.add(name)
            if not any(fnmatch.fnmatchcase(spath, g) for g in paths):
                raise SyncError(f"source {sid}: skill {name} path {spath} matches no glob")
            src.skills.append(SkillDecl(name, spath, str(sk.get("trigger", ""))))
        if not src.skills:
            raise SyncError(f"source {sid}: declares no skill")
        sources.append(src)
    return sources


def package_version() -> str:
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


# ------------------------------------------------------------------- fetch


def _git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1"}
    return subprocess.run(  # nosec B603 B607
        ["git", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        check=check,
    )


def fetch_files(src: Source, wanted: list[str] | None = None) -> dict[str, bytes]:
    """Return {path: bytes} for the license and every file the source's skills need.

    The pin is fetched into a throwaway repository and read with ``cat-file``;
    nothing is checked out or executed.
    """
    with tempfile.TemporaryDirectory(prefix="upstream-") as tmp:
        work = Path(tmp)
        _git(["init", "-q"], work)
        fetched = _git(
            ["fetch", "-q", "--depth", "1", src.repository, src.commit], work, check=False
        )
        if fetched.returncode != 0:
            _git(["fetch", "-q", src.repository, "+refs/heads/*:refs/remotes/o/*"], work)
        resolved = _git(["rev-parse", f"{src.commit}^{{commit}}"], work, check=False)
        if resolved.returncode != 0 or resolved.stdout.decode().strip() != src.commit:
            raise SyncError(f"source {src.id}: commit {src.commit} not found upstream")
        listing = _git(["ls-tree", "-r", "--name-only", "-z", src.commit], work)
        tree = [p for p in listing.stdout.decode().split("\0") if p]
        needed: set[str] = {src.license_path}
        for sk in src.skills:
            if src.transform == "command-md":
                needed.add(sk.path)
            else:
                prefix = sk.path.rstrip("/") + "/"
                needed.update(p for p in tree if p.startswith(prefix))
        files: dict[str, bytes] = {}
        for p in sorted(needed):
            if p not in tree:
                raise SyncError(f"source {src.id}: {p} missing at {src.commit}")
            files[p] = _git(["cat-file", "blob", f"{src.commit}:{p}"], work).stdout
        return files


def resolve_latest(src: Source) -> str:
    out = subprocess.run(  # nosec B603 B607
        ["git", "ls-remote", src.repository, f"refs/heads/{src.track}"],
        capture_output=True,
        check=False,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    line = out.stdout.decode().split("\n", 1)[0].split()
    if out.returncode != 0 or not line or not SHA_RE.match(line[0]):
        raise SyncError(f"source {src.id}: cannot resolve branch {src.track}")
    return line[0]


# ----------------------------------------------------------------- render


def _digest(files: dict[str, bytes]) -> str:
    h = hashlib.sha256()
    for p in sorted(files):
        h.update(p.encode() + b"\0" + files[p] + b"\0")
    return h.hexdigest()


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise SyncError("upstream file has no frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise SyncError("upstream frontmatter is not closed")
    return text[4:end], text[end + 5 :]


def _unquote(value: str) -> str:
    value = value.strip()
    if value[:1] in ('"', "'") and value[-1:] == value[:1] and len(value) > 1:
        return json.loads(value) if value[0] == '"' else value[1:-1]
    return value


def _command_fields(front: str) -> tuple[str, str]:
    """Return (description, sh script) from a command prompt's frontmatter."""
    desc = ""
    script = ""
    in_scripts = False
    for line in front.split("\n"):
        if re.match(r"^description:", line):
            desc = _unquote(line.split(":", 1)[1])
            in_scripts = False
        elif re.match(r"^scripts:\s*$", line):
            in_scripts = True
        elif in_scripts and re.match(r"^\s+sh:", line):
            script = _unquote(line.split(":", 1)[1])
        elif re.match(r"^\S", line):
            in_scripts = False
    if not desc or desc in (">", "|", ">-", "|-"):
        raise SyncError("command prompt needs a one-line description")
    return desc, script


def render_command(src: Source, sk: SkillDecl, raw: bytes, version: str) -> bytes:
    """Convert a command prompt into SKILL.md (deterministic)."""
    front, body = _split_frontmatter(raw.decode("utf-8"))
    desc, script = _command_fields(front)
    if "{SCRIPT}" in body and not script:
        raise SyncError(f"{sk.path}: {{SCRIPT}} used but no sh script declared")
    body = body.replace("{SCRIPT}", src.script_prefix + script)
    body = body.replace("{ARGS}", "$ARGUMENTS")
    body = re.sub(
        r"__SPECKIT_COMMAND_([A-Z_]+)__",
        lambda m: "speckit-" + m.group(1).lower().replace("_", "-"),
        body,
    )
    description = desc.rstrip(".") + "."
    if sk.trigger:
        description += " " + sk.trigger.strip()
    if len(description) > 1024:
        raise SyncError(f"{sk.name}: description exceeds 1024 characters")
    head = "\n".join(
        [
            "---",
            f"name: {sk.name}",
            "domain: development",
            "skill_type: skill",
            f"description: {json.dumps(description)}",
            f"license: {src.license}",
            "tags: [spec-kit, sdd, upstream]",
            "metadata:",
            f"  version: '{version}'",
            "  author: GitHub Spec Kit contributors",
            f"  upstream: {src.repository}",
            "---",
            "",
            f"# {sk.name}",
            "",
            "",
        ]
    )
    return (head + body.lstrip("\n").rstrip("\n") + "\n").encode("utf-8")


def render_skill_md(
    src: Source, sk: SkillDecl, files: dict[str, bytes], version: str
) -> dict[str, bytes]:
    """Copy a SKILL.md directory as-is, setting only metadata.version from our package."""
    prefix = sk.path.rstrip("/") + "/"
    out = {p[len(prefix) :]: b for p, b in files.items() if p.startswith(prefix)}
    if "SKILL.md" not in out:
        raise SyncError(f"{sk.name}: {sk.path} has no SKILL.md")
    text = out["SKILL.md"].decode("utf-8")
    front, body = _split_frontmatter(text)
    lines = [ln for ln in front.split("\n") if not re.match(r"^\s*version:", ln)]
    meta = next((i for i, ln in enumerate(lines) if re.match(r"^metadata:\s*$", ln)), None)
    if meta is None:
        lines += ["metadata:", f"  version: '{version}'"]
    else:
        lines.insert(meta + 1, f"  version: '{version}'")
    out["SKILL.md"] = ("---\n" + "\n".join(lines) + "\n---\n" + body).encode("utf-8")
    return out


@dataclass
class Overlay:
    rel: str
    mode: str
    match: str
    dest: str
    body: str
    digest: str


def load_overlays(name: str) -> list[Overlay]:
    folder = OVERLAYS_DIR / name
    if not folder.is_dir():
        return []
    result = []
    for path in sorted(folder.glob("*.md")):
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if not text.startswith("---\n"):
            raise SyncError(f"overlay {path.name}: header with mode is required")
        head, body = _split_frontmatter(text)
        fields = {}
        for line in head.split("\n"):
            if line.strip():
                key, _, val = line.partition(":")
                fields[key.strip()] = _unquote(val)
        mode = fields.get("mode", "")
        if mode not in OVERLAY_MODES:
            raise SyncError(f"overlay {name}/{path.name}: mode must be one of {OVERLAY_MODES}")
        if mode in ("replace", "insert-after") and not fields.get("match"):
            raise SyncError(f"overlay {name}/{path.name}: {mode} needs match")
        if mode == "file" and not fields.get("dest"):
            raise SyncError(f"overlay {name}/{path.name}: file needs dest")
        result.append(
            Overlay(
                rel=f"overlays/{name}/{path.name}",
                mode=mode,
                match=fields.get("match", ""),
                dest=fields.get("dest", ""),
                body=body.strip("\n"),
                digest=hashlib.sha256(raw).hexdigest(),
            )
        )
    return result


def apply_overlays(skill_md: str, overlays: list[Overlay], extra: dict[str, bytes]) -> str:
    """Merge overlays in filename order; the result is a pure function of the inputs."""
    for ov in overlays:
        if ov.mode == "file":
            if ov.dest.startswith("/") or ".." in ov.dest.split("/") or ov.dest == "SKILL.md":
                raise SyncError(f"{ov.rel}: unsafe dest {ov.dest}")
            extra[ov.dest] = (ov.body + "\n").encode("utf-8")
        elif ov.mode == "append":
            skill_md = skill_md.rstrip("\n") + "\n\n" + ov.body + "\n"
        elif ov.mode == "prepend":
            front, body = _split_frontmatter(skill_md)
            lines = body.lstrip("\n").split("\n", 1)
            title, rest = (lines[0], lines[1] if len(lines) > 1 else "")
            if title.startswith("# "):
                skill_md = f"---\n{front}\n---\n\n{title}\n\n{ov.body}\n\n{rest.lstrip(chr(10))}"
            else:
                skill_md = f"---\n{front}\n---\n\n{ov.body}\n\n{body.lstrip(chr(10))}"
        else:
            lines = skill_md.split("\n")
            hits = [i for i, ln in enumerate(lines) if ln.strip() == ov.match.strip()]
            if len(hits) != 1:
                raise SyncError(f"{ov.rel}: match must hit exactly one line, hit {len(hits)}")
            i = hits[0]
            block = ov.body.split("\n")
            lines[i : i + 1] = block if ov.mode == "replace" else [lines[i], *block]
            skill_md = "\n".join(lines)
    return skill_md


def render_provenance(
    src: Source, sk: SkillDecl, source_digest: str, overlays: list[Overlay], date: str
) -> str:
    ov = (
        "\n".join(f"  - `{o.rel}` (sha256 {o.digest[:16]})" for o in overlays)
        if overlays
        else "  - none"
    )
    return (
        f"# Upstream provenance: {sk.name}\n\n"
        "This skill is vendored. Do not edit it by hand: put local changes in an overlay.\n\n"
        f"- Source: {src.repository}\n"
        f"- Pinned commit: `{src.commit}`\n"
        f"- Path: `{sk.path}`\n"
        f"- License: {src.license} (the upstream license text is in `{LICENSE_FILE}`)\n"
        f"- Transform: `{src.transform}`\n"
        f"- Synced: {date}\n"
        f"- Source digest: sha256:{source_digest}\n"
        f"- Local overlays:\n{ov}\n"
        "\nRefresh with `python scripts/sync_upstream_skills.py --update "
        f"{src.id}`; verify with `--check`.\n"
    )


def render_skill(
    src: Source,
    sk: SkillDecl,
    snapshot: dict[str, bytes],
    version: str,
    date: str,
) -> dict[str, bytes]:
    """Return every file of the skill folder, keyed by relative path."""
    if src.transform == "command-md":
        files = {"SKILL.md": render_command(src, sk, snapshot[sk.path], version)}
        digest_files = {sk.path: snapshot[sk.path]}
    else:
        files = render_skill_md(src, sk, snapshot, version)
        prefix = sk.path.rstrip("/") + "/"
        digest_files = {p: b for p, b in snapshot.items() if p.startswith(prefix)}
    overlays = load_overlays(sk.name)
    extra: dict[str, bytes] = {}
    merged = apply_overlays(files["SKILL.md"].decode("utf-8"), overlays, extra)
    files["SKILL.md"] = merged.encode("utf-8")
    files.update(extra)
    files[LICENSE_FILE] = snapshot[src.license_path]
    files[PROVENANCE] = render_provenance(
        src, sk, _digest(digest_files), overlays, date
    ).encode("utf-8")
    return files


# ------------------------------------------------------------ disk and ops


def _read_dir(folder: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(folder)): p.read_bytes()
        for p in sorted(folder.rglob("*"))
        if p.is_file()
    }


def _recorded_date(skill_dir: Path) -> str | None:
    prov = skill_dir / PROVENANCE
    if not prov.is_file():
        return None
    found = re.search(r"^- Synced: (\S+)$", prov.read_text(encoding="utf-8"), re.M)
    return found.group(1) if found else None


def read_snapshot(src: Source, root: Path | None = None) -> dict[str, bytes]:
    base = (root or SNAPSHOT_DIR) / src.id
    if not base.is_dir():
        raise SyncError(f"source {src.id}: snapshot {base} is missing; run the sync")
    return {str(p.relative_to(base)): p.read_bytes() for p in base.rglob("*") if p.is_file()}


def write_snapshot(src: Source, files: dict[str, bytes], root: Path | None = None) -> None:
    base = (root or SNAPSHOT_DIR) / src.id
    if base.exists():
        shutil.rmtree(base)
    for p, data in files.items():
        dest = base / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


def sync_source(src: Source, version: str, today: str | None = None) -> None:
    files = fetch_files(src)
    write_snapshot(src, files)
    stamp = today or datetime.date.today().isoformat()
    for sk in src.skills:
        skill_dir = SKILLS_DIR / sk.name
        previous = _recorded_date(skill_dir)
        rendered = render_skill(src, sk, files, version, stamp)
        if previous and skill_dir.is_dir():
            kept = render_skill(src, sk, files, version, previous)
            if kept == _read_dir(skill_dir):
                rendered = kept
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        for rel, data in rendered.items():
            dest = skill_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)


def check_source(src: Source, version: str, verify_pin: bool = False) -> list[str]:
    """Return drift findings for one source; an empty list means in sync."""
    problems: list[str] = []
    try:
        snapshot = read_snapshot(src)
    except SyncError as exc:
        return [str(exc)]
    if verify_pin:
        try:
            upstream = fetch_files(src)
        except SyncError as exc:
            return [str(exc)]
        if upstream != snapshot:
            problems.append(f"{src.id}: snapshot differs from upstream at the pin")
    for sk in src.skills:
        skill_dir = SKILLS_DIR / sk.name
        if not skill_dir.is_dir():
            problems.append(f"{sk.name}: vendored skill folder is missing")
            continue
        try:
            expected = render_skill(
                src, sk, snapshot, version, _recorded_date(skill_dir) or "unknown"
            )
        except (SyncError, KeyError) as exc:
            problems.append(f"{sk.name}: cannot render from snapshot: {exc}")
            continue
        actual = _read_dir(skill_dir)
        for rel in sorted(set(expected) | set(actual)):
            if expected.get(rel) != actual.get(rel):
                problems.append(
                    f"{sk.name}/{rel}: differs from pinned source plus overlays "
                    "(put local changes in universal_skills/overlays/)"
                )
    return problems


def set_pin(commit: str, source_id: str, path: Path | None = None) -> None:
    """Rewrite the commit of one source in place, keeping comments and layout."""
    path = path or MANIFEST
    lines = path.read_text(encoding="utf-8").split("\n")
    in_source = False
    done = False
    for i, line in enumerate(lines):
        if line.strip() == "[[source]]":
            in_source = False
        if re.match(rf'^id\s*=\s*"{re.escape(source_id)}"\s*$', line):
            in_source = True
        elif in_source and re.match(r"^commit\s*=", line):
            lines[i] = f'commit = "{commit}"'
            done = True
            break
    if not done:
        raise SyncError(f"cannot rewrite pin of {source_id}")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--source", help="limit to one source id")
    ap.add_argument("--check", action="store_true", help="fail on drift (offline)")
    ap.add_argument("--verify-pin", action="store_true", help="with --check, compare upstream")
    ap.add_argument("--update", metavar="ID", help="bump the pin to upstream's latest, re-sync")
    args = ap.parse_args(argv)
    try:
        sources = load_manifest()
        version = package_version()
        if args.update:
            src = next((s for s in sources if s.id == args.update), None)
            if src is None:
                raise SyncError(f"unknown source {args.update}")
            latest = resolve_latest(src)
            if latest != src.commit:
                set_pin(latest, src.id)
                print(f"{src.id}: {src.commit[:12]} -> {latest[:12]}")
            else:
                print(f"{src.id}: already at upstream latest {latest[:12]}")
            sources = load_manifest()
            args.source = src.id
        selected = [s for s in sources if not args.source or s.id == args.source]
        if args.source and not selected:
            raise SyncError(f"unknown source {args.source}")
        if args.check:
            findings = [
                f for s in selected for f in check_source(s, version, args.verify_pin)
            ]
            for f in findings:
                print(f"DRIFT: {f}", file=sys.stderr)
            return 1 if findings else 0
        for s in selected:
            sync_source(s, version)
            print(f"{s.id}: synced {len(s.skills)} skill(s) at {s.commit[:12]}")
        return 0
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

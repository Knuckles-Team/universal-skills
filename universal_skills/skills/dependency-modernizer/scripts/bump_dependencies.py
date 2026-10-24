#!/usr/bin/env python3
"""Bump pyproject.toml dependencies to their newest PyPI versions, across any
set of repos.

For every ``[project].dependencies`` entry and every list under
``[project.optional-dependencies]`` in each target ``pyproject.toml``, resolve
the newest version on PyPI and rewrite the entry to ``>=<latest>`` (dropping
any upper-bound cap unless ``--keep-caps``). ``[project].version`` and
``[build-system]`` are never touched. Editing goes through ``tomlkit`` so
every byte outside the changed specifiers — comments, quoting, indentation,
key order — survives the round trip.

An entry is left byte-for-byte alone (and counted, not silently dropped) when:

* it names a workspace/intra-repo member — auto-detected by scanning
  ``--workspace-root`` (if given) for sibling ``[project].name`` values, plus
  any ``--skip`` name;
* its trailing ``#`` comment mentions "CVE" — treated as a pinned security
  floor;
* its specifier is complex — a direct URL/VCS reference (``@``) or an
  environment marker (``;``).

This is only the bump. It does not run ``uv lock``/``pip-compile`` or a test
suite — do that separately per repo afterward to reconcile the lockfile and
catch anything the new versions break.

CLI:
    python bump_dependencies.py <PATHS...> [--dry-run | --no-dry-run] [--commit]
        [--branch-prefix P] [--workspace-root DIR] [--skip NAME...]
        [--keep-caps] [--include-prerelease]

``--dry-run`` defaults on (edits nothing; prints the JSON summary of what
WOULD change). Pass ``--no-dry-run`` to write the files in place, or
``--commit`` to also branch off ``main``, commit the repo's ``pyproject.toml``,
and restore ``main`` (repos with no change are skipped) — ``--commit`` alone
is enough to write + commit; an explicit ``--dry-run`` always wins and
previews instead, even combined with ``--commit``.
"""

from __future__ import annotations

import argparse
import glob as glob_module
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - repo floor is 3.11+; kept for standalone reuse
    import tomli as tomllib

try:
    import tomlkit
except ImportError:
    print(
        "Error: Missing required dependency 'tomlkit' for the "
        "'dependency-modernizer' skill.",
        file=sys.stderr,
    )
    print(
        "Install it into your active environment, e.g.: pip install tomlkit",
        file=sys.stderr,
    )
    sys.exit(1)


PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"
DEFAULT_BRANCH_PREFIX = "chore/bump-deps-"
_REQUEST_TIMEOUT_S = 15

# name[extras] at the front of a PEP 508 dependency string.
_DEP_HEAD_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?P<extras>\[[^\]]*\])?"
)
# One specifier clause, e.g. ">=1.2.3" or "<2.0.0".
_CLAUSE_RE = re.compile(r"(==|>=|<=|~=|!=|>|<)\s*([A-Za-z0-9_.\-+!]+)")
# PEP 440-ish pre-release / dev suffixes (best-effort; not a full parser).
_PRE_RE = re.compile(
    r"(?:^|[._-])(a|alpha|b|beta|c|rc|pre|preview)\.?(\d*)$", re.IGNORECASE
)
_DEV_RE = re.compile(r"(?:^|[._-])dev\.?(\d*)$", re.IGNORECASE)
_RELEASE_RE = re.compile(r"^v?(\d+(?:\.\d+)*)")
_PRE_RANK = {
    "a": 0,
    "alpha": 0,
    "b": 1,
    "beta": 1,
    "c": 2,
    "rc": 2,
    "pre": 2,
    "preview": 2,
}


# --------------------------------------------------------------------------- #
# PEP 508 / spec parsing helpers                                              #
# --------------------------------------------------------------------------- #


def normalize(name: str) -> str:
    """PEP 503 normalized comparison key (case/`-`/`_`/`.`-insensitive)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_dep_head(dep: str) -> tuple[str, str]:
    """Return ``(name, extras_text)`` parsed off the front of a dependency string."""
    m = _DEP_HEAD_RE.match(dep.strip())
    if not m:
        return dep.strip(), ""
    return m.group("name"), m.group("extras") or ""


def is_complex_spec(dep: str) -> bool:
    """True for a direct URL/VCS reference (``@``) or an environment marker (``;``)."""
    return "@" in dep or ";" in dep


def find_upper_cap(dep: str) -> str | None:
    """Return the first ``<``/``<=`` clause text (e.g. ``<2.0.0``), or ``None``."""
    name, extras = parse_dep_head(dep)
    rest = dep.strip()[len(name) + len(extras) :]
    for op, val in _CLAUSE_RE.findall(rest):
        if op in ("<", "<="):
            return f"{op}{val}"
    return None


def compute_new_dep_string(dep: str, *, latest: str, keep_caps: bool) -> str:
    """Return the rewritten dependency string: ``name[extras]>=<latest>``.

    With ``keep_caps``, an existing upper-bound clause is appended verbatim
    after the new floor. Markers/URLs never reach here — callers must have
    already routed those through :func:`is_complex_spec`.
    """
    name, extras = parse_dep_head(dep)
    new_spec = f">={latest}"
    if keep_caps:
        cap = find_upper_cap(dep)
        if cap:
            new_spec += f",{cap}"
    return f"{name}{extras}{new_spec}"


def cve_protected_values(raw_text: str) -> set[str]:
    """Exact dependency-string values whose source line has a "CVE" comment."""
    protected: set[str] = set()
    for line in raw_text.splitlines():
        if "#" not in line:
            continue
        code, _, comment = line.partition("#")
        if "cve" not in comment.lower():
            continue
        for quote in ('"', "'"):
            start = 0
            while True:
                i = code.find(quote, start)
                if i == -1:
                    break
                j = code.find(quote, i + 1)
                if j == -1:
                    break
                protected.add(code[i + 1 : j])
                start = j + 1
    return protected


# --------------------------------------------------------------------------- #
# PyPI resolution                                                             #
# --------------------------------------------------------------------------- #


def _fetch_pypi_json(name: str) -> dict[str, Any] | None:
    """GET the PyPI JSON metadata for *name*. Returns ``None`` on any failure.

    The sole network boundary in this module — tests mock this function so no
    real HTTP call is ever made from the test suite.
    """
    url = PYPI_JSON_URL.format(name=name)
    try:
        with urllib.request.urlopen(url, timeout=_REQUEST_TIMEOUT_S) as resp:  # noqa: S310
            if resp.status != 200:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def _release_tuple(version: str) -> tuple[int, ...]:
    m = _RELEASE_RE.match(version.strip())
    return tuple(int(part) for part in m.group(1).split(".")) if m else (0,)


def _prerelease_rank(version: str) -> tuple[int, int] | None:
    """``None`` for a final/post release; else an ascending ``(rank, num)`` marker."""
    dev = _DEV_RE.search(version)
    if dev:
        return (-1, int(dev.group(1)) if dev.group(1) else 0)
    pre = _PRE_RE.search(version)
    if pre:
        label, num = pre.group(1).lower(), pre.group(2)
        return (_PRE_RANK.get(label, 0), int(num) if num else 0)
    return None


def pick_latest_from_releases(
    releases: dict[str, list[dict[str, Any]]], *, include_prerelease: bool
) -> str | None:
    """Pick the newest version key out of a PyPI ``releases`` mapping."""
    candidates = [
        v
        for v, files in releases.items()
        if files and not all(f.get("yanked") for f in files)
    ]
    if not include_prerelease:
        candidates = [v for v in candidates if _prerelease_rank(v) is None]
    if not candidates:
        return None
    max_release = max(_release_tuple(v) for v in candidates)
    at_max = [v for v in candidates if _release_tuple(v) == max_release]
    finals = [v for v in at_max if _prerelease_rank(v) is None]
    if finals:
        return max(finals)
    # Every entry here has a non-None rank (the `finals` branch above is the
    # only place a None rank is possible); the `or` fallback only satisfies
    # the type checker, it never actually triggers.
    return max(at_max, key=lambda v: _prerelease_rank(v) or (0, 0))


def latest_version(name: str, *, include_prerelease: bool = False) -> str | None:
    """Latest version of *name* on PyPI, or ``None`` if it cannot be resolved."""
    data = _fetch_pypi_json(name)
    if data is None:
        return None
    if include_prerelease:
        picked = pick_latest_from_releases(
            data.get("releases") or {}, include_prerelease=True
        )
        if picked:
            return picked
    # PyPI's own "latest" (stable-preferring; falls back to a prerelease only
    # when a project has never shipped a stable release).
    return data.get("info", {}).get("version") or None


# --------------------------------------------------------------------------- #
# Target resolution (repo dirs / explicit files / globs)                      #
# --------------------------------------------------------------------------- #


def resolve_targets(paths: list[str]) -> tuple[list[Path], list[str]]:
    """Expand PATHS into concrete ``pyproject.toml`` files. Never raises."""
    resolved: dict[Path, None] = {}
    errors: list[str] = []
    for raw in paths:
        if any(ch in raw for ch in "*?["):
            matches = sorted(glob_module.glob(raw, recursive=True))
            if not matches:
                errors.append(f"glob matched nothing: {raw}")
                continue
            candidates = [Path(m) for m in matches]
        else:
            candidates = [Path(raw)]

        for candidate in candidates:
            if not candidate.exists():
                errors.append(f"path not found: {candidate}")
                continue
            if candidate.is_dir():
                pyproject = candidate / "pyproject.toml"
                if not pyproject.is_file():
                    errors.append(f"no pyproject.toml in {candidate}")
                    continue
                resolved[pyproject.resolve()] = None
            elif candidate.name == "pyproject.toml":
                resolved[candidate.resolve()] = None
            else:
                errors.append(f"not a pyproject.toml: {candidate}")
    return list(resolved.keys()), errors


def discover_workspace_members(workspace_root: str | None) -> set[str]:
    """Normalized ``[project].name`` values of every pyproject.toml under *workspace_root*."""
    if not workspace_root:
        return set()
    root = Path(workspace_root)
    names: set[str] = set()
    if not root.is_dir():
        return names
    for pyproject in root.rglob("pyproject.toml"):
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            continue
        name = data.get("project", {}).get("name")
        if name:
            names.add(normalize(str(name)))
    return names


# --------------------------------------------------------------------------- #
# Core bump                                                                   #
# --------------------------------------------------------------------------- #


@dataclass
class RepoResult:
    path: str
    repo: str
    bumped: list[dict[str, str]] = field(default_factory=list)
    skipped_member: list[str] = field(default_factory=list)
    skipped_cve: list[str] = field(default_factory=list)
    skipped_complex: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    changed: bool = False
    new_text: str = ""

    def summary(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "changed": self.changed,
            "bumped": self.bumped,
            "skipped_member": self.skipped_member,
            "skipped_cve": self.skipped_cve,
            "skipped_complex": self.skipped_complex,
            "errors": self.errors,
        }


def _iter_dependency_arrays(doc: Any) -> list[tuple[str, Any]]:
    """``(section_label, tomlkit Array)`` for every dependency list to scan."""
    project = doc.get("project")
    if project is None:
        return []
    arrays: list[tuple[str, Any]] = []
    deps = project.get("dependencies")
    if deps is not None:
        arrays.append(("project.dependencies", deps))
    for group_name, group_list in (project.get("optional-dependencies") or {}).items():
        arrays.append((f"project.optional-dependencies.{group_name}", group_list))
    return arrays


def bump_pyproject(
    path: Path,
    *,
    workspace_members: AbstractSet[str] = frozenset(),
    skip_names: AbstractSet[str] = frozenset(),
    keep_caps: bool = False,
    include_prerelease: bool = False,
) -> RepoResult:
    """Bump one ``pyproject.toml``. Reads and computes only — never writes."""
    repo = path.parent.name
    result = RepoResult(path=str(path), repo=repo)

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        result.errors.append(f"cannot read {path}: {exc}")
        return result

    try:
        doc = tomlkit.parse(raw_text)
    except Exception as exc:  # noqa: BLE001 - any tomlkit parse failure is per-repo, not fatal
        result.errors.append(f"cannot parse {path}: {type(exc).__name__}: {exc}")
        return result

    own_name = (doc.get("project") or {}).get("name") or ""
    effective_skip = {normalize(n) for n in skip_names} | workspace_members
    if own_name:
        effective_skip.add(normalize(str(own_name)))

    cve_values = cve_protected_values(raw_text)

    for section, array in _iter_dependency_arrays(doc):
        for idx, raw_dep in enumerate(list(array)):
            dep = str(raw_dep)
            name, _extras = parse_dep_head(dep)
            if not name:
                continue

            if dep in cve_values:
                result.skipped_cve.append(dep)
                continue
            if is_complex_spec(dep):
                result.skipped_complex.append(dep)
                continue
            if normalize(name) in effective_skip:
                result.skipped_member.append(dep)
                continue

            try:
                latest = latest_version(name, include_prerelease=include_prerelease)
            except Exception as exc:  # noqa: BLE001 - one bad package must not abort the batch
                result.errors.append(f"{name}: {type(exc).__name__}: {exc}")
                continue
            if not latest:
                result.errors.append(f"{name}: could not resolve a version on PyPI")
                continue

            new_dep = compute_new_dep_string(dep, latest=latest, keep_caps=keep_caps)
            if new_dep == dep:
                continue

            array[idx] = new_dep
            result.bumped.append(
                {"section": section, "package": name, "from": dep, "to": new_dep}
            )

    result.changed = bool(result.bumped)
    result.new_text = tomlkit.dumps(doc) if result.changed else raw_text
    return result


# --------------------------------------------------------------------------- #
# --commit: branch off main, commit, restore main                            #
# --------------------------------------------------------------------------- #


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed "git" argv, no shell
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _err_tail(exc: Exception) -> str:
    if isinstance(exc, subprocess.CalledProcessError):
        lines = (exc.stderr or "").strip().splitlines()
        return lines[-1] if lines else str(exc)
    return str(exc)


def commit_repo(
    pyproject_path: Path, new_text: str, branch_prefix: str, bumped_count: int
) -> str | None:
    """Branch off ``main``, write + commit, restore ``main``. Returns an error string, or ``None``."""
    repo_dir = pyproject_path.parent
    branch = f"{branch_prefix}{repo_dir.name}"
    noun = "dependency" if bumped_count == 1 else "dependencies"

    try:
        _run_git(["checkout", "-b", branch, "main"], repo_dir)
    except (subprocess.CalledProcessError, OSError) as exc:
        return f"checkout -b {branch} off main failed: {_err_tail(exc)}"

    try:
        pyproject_path.write_text(new_text, encoding="utf-8")
        _run_git(["add", "pyproject.toml"], repo_dir)
        _run_git(
            ["commit", "-m", f"chore: bump {bumped_count} {noun} to latest"],
            repo_dir,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        try:
            _run_git(["checkout", "main"], repo_dir)
        except (subprocess.CalledProcessError, OSError):
            pass
        return f"commit on {branch} failed: {_err_tail(exc)}"

    try:
        _run_git(["checkout", "main"], repo_dir)
    except (subprocess.CalledProcessError, OSError) as exc:
        return f"committed on {branch} but failed to restore main: {_err_tail(exc)}"
    return None


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #


def run(
    paths: list[str],
    *,
    dry_run: bool = True,
    commit: bool = False,
    branch_prefix: str = DEFAULT_BRANCH_PREFIX,
    workspace_root: str | None = None,
    skip: list[str] | None = None,
    keep_caps: bool = False,
    include_prerelease: bool = False,
) -> dict[str, Any]:
    """Bump every resolved pyproject.toml and return the JSON-ready summary.

    ``dry_run`` always wins: when it is true, nothing is written and nothing is
    committed, regardless of ``commit``.
    """
    files, path_errors = resolve_targets(paths)
    workspace_members = discover_workspace_members(workspace_root)
    skip_names = set(skip or [])

    totals = {
        "bumped": 0,
        "skipped_member": 0,
        "skipped_cve": 0,
        "skipped_complex": 0,
        "errors": 0,
    }
    repos: dict[str, Any] = {}

    for pyproject_path in files:
        result = bump_pyproject(
            pyproject_path,
            workspace_members=workspace_members,
            skip_names=skip_names,
            keep_caps=keep_caps,
            include_prerelease=include_prerelease,
        )

        if result.changed and not dry_run:
            if commit:
                err = commit_repo(
                    pyproject_path, result.new_text, branch_prefix, len(result.bumped)
                )
                if err:
                    result.errors.append(err)
            else:
                pyproject_path.write_text(result.new_text, encoding="utf-8")

        totals["bumped"] += len(result.bumped)
        totals["skipped_member"] += len(result.skipped_member)
        totals["skipped_cve"] += len(result.skipped_cve)
        totals["skipped_complex"] += len(result.skipped_complex)
        totals["errors"] += len(result.errors)
        repos[result.repo] = result.summary()

    totals["errors"] += len(path_errors)
    return {
        "dry_run": dry_run,
        "commit": commit,
        "totals": totals,
        "path_errors": path_errors,
        "repos": repos,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Bump pyproject.toml dependencies to their newest PyPI versions "
            "across any set of repos."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATHS",
        help="Repo dirs (auto-finds pyproject.toml), explicit pyproject.toml paths, or globs",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Preview only, write nothing (the default when neither --dry-run/"
            "--no-dry-run nor --commit is given). Pass --no-dry-run to edit "
            "files in place. --commit alone also disables dry-run; an "
            "explicit --dry-run always wins, even combined with --commit."
        ),
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help=(
            "Additionally create '<branch-prefix><repo-name>' off main, commit "
            "the repo's pyproject.toml, and restore main. Repos with no change "
            "are skipped."
        ),
    )
    parser.add_argument(
        "--branch-prefix",
        default=DEFAULT_BRANCH_PREFIX,
        help=f"Branch name prefix for --commit (default: {DEFAULT_BRANCH_PREFIX!r})",
    )
    parser.add_argument(
        "--workspace-root",
        default=None,
        metavar="DIR",
        help="Directory to scan for sibling [project].name values to auto-skip as workspace members",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=[],
        metavar="NAME",
        help="Additional dependency names to skip, same as an auto-detected workspace member",
    )
    parser.add_argument(
        "--keep-caps",
        action="store_true",
        help="Preserve an existing upper-bound cap instead of dropping it",
    )
    parser.add_argument(
        "--include-prerelease",
        action="store_true",
        help="Consider prereleases when resolving each package's newest version",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    effective_dry_run = (not args.commit) if args.dry_run is None else args.dry_run

    summary = run(
        args.paths,
        dry_run=effective_dry_run,
        commit=args.commit,
        branch_prefix=args.branch_prefix,
        workspace_root=args.workspace_root,
        skip=args.skip,
        keep_caps=args.keep_caps,
        include_prerelease=args.include_prerelease,
    )
    print(json.dumps(summary, indent=2))
    return 1 if summary["totals"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

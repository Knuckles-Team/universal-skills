#!/usr/bin/env python3
"""CE-042: Apply dependency-version updates to a project.

The companion *write* path to ``audit_dependencies.py`` (which is report-only).
Bumps dependency constraints in ``pyproject.toml`` and ``requirements.txt`` to the
latest versions on PyPI, losslessly (the only bytes that change are the version
operands inside each dependency string — comments, extras, markers, ordering and
formatting are preserved).

Default is a DRY RUN that prints a unified diff; pass ``--apply`` to write.

Levels (``--level``):
    patch  — only bump when the change is a patch (z in x.y.z)
    minor  — bump patch + minor                     (default)
    major  — bump everything, raising capped upper bounds where a new major exists

Reuses ``audit_dependencies._get_latest_version`` for the PyPI lookup so there is
exactly one place that talks to PyPI.

CONCEPT:CE-042 — Dependency Update Application
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse the single PyPI lookup helper (extend-before-invent).
try:
    from audit_dependencies import _get_latest_version
except ImportError:  # pragma: no cover - allow running from another cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audit_dependencies import _get_latest_version

try:
    from packaging.version import InvalidVersion, Version

    HAS_PACKAGING = True
except ImportError:  # pragma: no cover
    HAS_PACKAGING = False


_LEVEL_ORDER = {"patch": 0, "minor": 1, "major": 2}

# A dependency entry: name + optional [extras], then specifiers, then optional ; marker.
_DEP_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?P<extras>\[[^\]]*\])?"
    r"(?P<spec>[^;]*?)"
    r"(?P<marker>\s*;.*)?$"
)
# A single specifier clause, e.g. ">=1.2.3" or "<2.0.0".
_CLAUSE_RE = re.compile(r"\s*(==|>=|<=|~=|!=|>|<)\s*([^,\s]+)\s*")


def _change_level(old: str, new: str) -> str | None:
    """Return 'patch'|'minor'|'major' for old→new, or None if not an upgrade."""
    if not HAS_PACKAGING:
        return None
    try:
        o, n = Version(old), Version(new)
    except InvalidVersion:
        return None
    if n <= o:
        return None
    if n.major != o.major:
        return "major"
    if n.minor != o.minor:
        return "minor"
    return "patch"


def _parse_spec(spec: str) -> list[tuple[str, str]]:
    """Split a specifier string into (op, version) clauses."""
    return [(m.group(1), m.group(2)) for m in _CLAUSE_RE.finditer(spec or "")]


def _rebuild_spec(clauses: list[tuple[str, str]]) -> str:
    return ",".join(f"{op}{ver}" for op, ver in clauses)


def _new_spec_for(spec: str, latest: str, level: str) -> tuple[str | None, str | None]:
    """Compute a new specifier string for a dependency.

    Returns (new_spec, reason) where new_spec is None when no change applies.
    ``spec`` is the raw specifier text (may be empty for an unpinned dep).
    """
    if not HAS_PACKAGING:
        return None, None
    try:
        latest_v = Version(latest)
    except InvalidVersion:
        return None, None
    # Never pin to a pre-release (alpha/beta/rc/dev). PyPI's "latest" is a
    # pre-release for packages that only ship betas (e.g. opentelemetry's 0.63b1);
    # adding such a floor breaks resolution. Stay on stable.
    if latest_v.is_prerelease or latest_v.is_devrelease:
        return None, "skipped (latest is a pre-release)"

    clauses = _parse_spec(spec)
    lower_idx = next(
        (i for i, (op, _) in enumerate(clauses) if op in (">=", "~=", "==", ">")),
        None,
    )
    upper_idx = next(
        (i for i, (op, _) in enumerate(clauses) if op in ("<", "<=")), None
    )
    allow = _LEVEL_ORDER[level]

    # Unpinned (no floor): add a floor at latest.
    if lower_idx is None:
        new_clauses = clauses + [(">=", latest)]
        return _rebuild_spec(new_clauses), f"add floor >= {latest}"

    op, cur = clauses[lower_idx]
    change = _change_level(cur, latest)
    if change is None:
        return None, None  # already current or unparseable
    if _LEVEL_ORDER[change] > allow:
        return None, f"skipped ({change} > --level {level})"

    # Honour an upper cap unless we are explicitly raising it (major level only).
    if upper_idx is not None:
        cap_op, cap_ver = clauses[upper_idx]
        try:
            cap_v = Version(cap_ver)
        except InvalidVersion:
            cap_v = None
        if cap_v is not None and latest_v >= cap_v:
            if level != "major":
                return None, f"skipped (latest {latest} >= cap {cap_op}{cap_ver})"
            # Raise the cap to the next major above latest.
            new_cap = f"{latest_v.major + 1}.0"
            clauses[upper_idx] = ("<", new_cap)
            clauses[lower_idx] = (op if op != "==" else ">=", latest)
            return _rebuild_spec(clauses), f"raise cap to <{new_cap}, floor {latest}"

    clauses[lower_idx] = (op, latest)
    return _rebuild_spec(clauses), f"bump floor to {latest}"


def _update_dep_string(dep: str, latest: str, level: str) -> tuple[str | None, str | None, str]:
    """Return (new_dep_string|None, reason|None, pkg_name)."""
    m = _DEP_RE.match(dep.strip())
    if not m:
        return None, None, ""
    name = m.group("name")
    extras = m.group("extras") or ""
    spec = m.group("spec") or ""
    marker = m.group("marker") or ""
    new_spec, reason = _new_spec_for(spec, latest, level)
    if new_spec is None:
        return None, reason, name
    return f"{name}{extras}{new_spec}{marker}", reason, name


def _collect_pyproject_deps(path: Path) -> list[str]:
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return []
    deps: list[str] = list(data.get("project", {}).get("dependencies", []))
    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        deps.extend(group)
    return deps


def _dep_name(dep: str) -> str:
    m = _DEP_RE.match(dep.strip())
    return m.group("name") if m else dep.strip()


def _replace_in_text(text: str, old: str, new: str) -> tuple[str, bool]:
    """Replace a quoted dependency string (preferring exact quoted forms)."""
    for q in ('"', "'"):
        token = f"{q}{old}{q}"
        if token in text:
            return text.replace(token, f"{q}{new}{q}", 1), True
    # requirements.txt: bare, line-anchored.
    pat = re.compile(rf"(?m)^(\s*){re.escape(old)}(\s*(?:#.*)?)$")
    new_text, n = pat.subn(rf"\g<1>{new}\g<2>", text, count=1)
    return new_text, bool(n)


def apply_updates(
    root_dir: str = ".",
    level: str = "minor",
    only: set[str] | None = None,
    skip: set[str] | None = None,
    apply: bool = False,
    insecure: bool = False,
) -> dict:
    root = Path(root_dir).resolve()
    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"
    only = {p.lower() for p in (only or set())}
    skip = {p.lower() for p in (skip or set())}

    if not HAS_PACKAGING:
        return {"error": "packaging not available", "changes": [], "diffs": {}}

    # Never rewrite the project's own self-referential extras (e.g. a pyproject
    # that lists ``mypkg[owl]`` inside its own optional-dependencies). Bumping a
    # self-reference is meaningless and can break local/workspace resolution.
    if pyproject.exists():
        try:
            with open(pyproject, "rb") as f:
                own_name = tomllib.load(f).get("project", {}).get("name")
            if own_name:
                skip.add(own_name.lower())
        except Exception:
            pass

    # Gather candidate names from pyproject (authoritative) + requirements.
    pyproject_deps = _collect_pyproject_deps(pyproject) if pyproject.exists() else []
    req_lines: list[str] = []
    if requirements.exists():
        req_lines = [
            ln.strip()
            for ln in requirements.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith(("#", "-"))
        ]

    names = {_dep_name(d) for d in pyproject_deps} | {_dep_name(d) for d in req_lines}
    names = {n for n in names if n and n.lower() != "python"}
    if only:
        names = {n for n in names if n.lower() in only}
    names -= {n for n in names if n.lower() in skip}

    # Fetch latest versions concurrently (reusing the audit helper).
    latest: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(_get_latest_version, n, insecure): n for n in names}
        for fut in as_completed(futs):
            info = fut.result()
            if info and info.get("latest") not in (None, "NOT_FOUND", "unknown"):
                latest[futs[fut]] = info["latest"]

    changes: list[dict] = []
    diffs: dict[str, str] = {}

    def _process(path: Path, deps_in_text: list[str], label: str) -> None:
        if not path.exists():
            return
        text = path.read_text()
        new_text = text
        for dep in deps_in_text:
            name = _dep_name(dep)
            if name not in latest:
                continue
            new_dep, reason, _ = _update_dep_string(dep, latest[name], level)
            if not new_dep or new_dep == dep:
                continue
            replaced, ok = _replace_in_text(new_text, dep, new_dep)
            if ok:
                new_text = replaced
                changes.append(
                    {"file": label, "package": name, "from": dep, "to": new_dep, "reason": reason}
                )
        if new_text != text:
            diff = "".join(
                difflib.unified_diff(
                    text.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=f"a/{label}",
                    tofile=f"b/{label}",
                )
            )
            diffs[label] = diff
            if apply:
                path.write_text(new_text)

    _process(pyproject, pyproject_deps, "pyproject.toml")
    _process(requirements, req_lines, "requirements.txt")

    return {
        "root": str(root),
        "level": level,
        "applied": apply,
        "packages_checked": len(names),
        "changes": changes,
        "change_count": len(changes),
        "diffs": diffs,
    }


def _self_test() -> int:
    """Pure, network-free unit checks on the spec-rewriting core."""
    cases = [
        # (spec, latest, level, expected_new_spec_or_None)
        (">=2.10.0", "2.13.4", "minor", ">=2.13.4"),
        (">=48.0.0", "49.0.0", "minor", None),  # major blocked at minor level
        (">=48.0.0", "49.0.0", "major", ">=49.0.0"),
        (">=1.90.0,<2.0.0", "1.107.0", "minor", ">=1.107.0,<2.0.0"),  # within cap
        (">=0.0.18,<0.1.0", "0.2.0", "minor", None),  # exceeds cap, not major
        (">=0.0.18,<0.1.0", "0.2.0", "major", ">=0.2.0,<1.0"),  # cap raised
        ("", "1.2.3", "minor", ">=1.2.3"),  # unpinned → add floor
        (">=2.34.0", "2.34.0", "minor", None),  # already current
        ("", "0.63b1", "major", None),  # pre-release → never add a floor
        (">=1.0", "2.0rc1", "major", None),  # pre-release → never bump
    ]
    ok = True
    for spec, latest, level, expected in cases:
        got, _ = _new_spec_for(spec, latest, level)
        if got != expected:
            print(f"FAIL: spec={spec!r} latest={latest} level={level} -> {got!r} (want {expected!r})")
            ok = False
    # End-to-end string rewrite preserves extras + markers.
    dep = "pydantic[email]>=2.10.0"
    new_dep, _, _ = _update_dep_string(dep, "2.13.4", "minor")
    if new_dep != "pydantic[email]>=2.13.4":
        print(f"FAIL: extras rewrite -> {new_dep!r}")
        ok = False
    dep2 = "foo>=1.0; python_version < '3.12'"
    new_dep2, _, _ = _update_dep_string(dep2, "1.5", "minor")
    if new_dep2 != "foo>=1.5; python_version < '3.12'":
        print(f"FAIL: marker rewrite -> {new_dep2!r}")
        ok = False
    print("apply_dependency_updates self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply dependency-version updates")
    parser.add_argument("target", nargs="?", default=".", help="Project root")
    parser.add_argument(
        "--level", choices=["patch", "minor", "major"], default="minor",
        help="Maximum bump level to apply (default: minor)",
    )
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run diff)")
    parser.add_argument("--only", default="", help="Comma-separated package allow-list")
    parser.add_argument("--skip", default="", help="Comma-separated package skip-list")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL verification")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of diff")
    parser.add_argument("--self-test", action="store_true", help="Run offline self-test")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(_self_test())

    result = apply_updates(
        args.target,
        level=args.level,
        only={p.strip() for p in args.only.split(",") if p.strip()},
        skip={p.strip() for p in args.skip.split(",") if p.strip()},
        apply=args.apply,
        insecure=args.insecure,
    )
    if args.json:
        result_no_diffs = {k: v for k, v in result.items() if k != "diffs"}
        print(json.dumps(result_no_diffs, indent=2))
    else:
        for label, diff in result["diffs"].items():
            print(diff)
        verb = "Applied" if args.apply else "Would apply"
        print(f"\n{verb} {result['change_count']} change(s) at --level {args.level} "
              f"({result['packages_checked']} packages checked). "
              f"{'WRITTEN' if args.apply else 'DRY RUN — pass --apply to write.'}")

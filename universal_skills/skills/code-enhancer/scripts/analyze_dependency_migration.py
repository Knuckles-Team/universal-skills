#!/usr/bin/env python3
"""CE-043: Dependency migration intelligence.

Answers the two questions a version bump raises that a plain audit does NOT:
  1. **Deprecations to remove** — which deprecated/removed APIs does OUR code use
     after the upgrade? (static: changelog "Deprecated/Removed" ∩ our imported
     symbols; dynamic, opt-in: DeprecationWarnings our code triggers at import.)
  2. **New features to adopt** — what did the upgraded packages ADD in the version
     range we crossed, in the surface area we already use?

Reuses existing machinery (extend-before-invent):
  - ``audit_dependencies._get_latest_version`` / ``_get_installed_version`` / ``_compare_versions``
  - ``audit_changelog._get_dependency_changelog_url`` / ``_fetch_and_parse_changelog``

CONCEPT:CE-043 — Dependency Migration Intelligence
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from audit_dependencies import (
        _compare_versions,
        _get_installed_version,
        _get_latest_version,
        _parse_pyproject,
        _parse_requirements,
    )
except ImportError:  # pragma: no cover
    _get_latest_version = _get_installed_version = _compare_versions = None  # type: ignore
    _parse_pyproject = _parse_requirements = None  # type: ignore

try:
    from audit_changelog import _fetch_and_parse_changelog, _get_dependency_changelog_url
except ImportError:  # pragma: no cover
    _get_dependency_changelog_url = _fetch_and_parse_changelog = None  # type: ignore

_SKIP_DIRS = frozenset(
    {".venv", "venv", "__pycache__", "node_modules", ".git", "build", "dist", ".tox", "target"}
)


def _dist_to_import_names() -> dict[str, list[str]]:
    """Map a distribution name (lowercased) → its top-level import module names."""
    mapping: dict[str, list[str]] = {}
    try:
        import importlib.metadata as meta

        pkgs = meta.packages_distributions()  # import_name -> [dist, ...]
        for import_name, dists in pkgs.items():
            for dist in dists:
                mapping.setdefault(dist.lower(), []).append(import_name)
    except Exception:
        pass
    return mapping


def _imported_symbols(root: Path, module_names: set[str]) -> dict[str, set[str]]:
    """Find which symbols of the given top-level modules OUR code imports/uses.

    Returns module_name -> {used symbol names}. Captures ``from mod import X`` and
    ``import mod`` + ``mod.attr`` attribute access.
    """
    used: dict[str, set[str]] = {m: set() for m in module_names}
    if not module_names:
        return used
    for f in root.rglob("*.py"):
        if any(p in _SKIP_DIRS for p in f.parts):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"), filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        aliases: dict[str, str] = {}  # local alias -> top module
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top in module_names:
                    for a in node.names:
                        used[top].add(a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    top = a.name.split(".")[0]
                    if top in module_names:
                        aliases[a.asname or top] = top
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                top = aliases.get(node.value.id)
                if top:
                    used[top].add(node.attr)
    return used


def _versions_in_range(parsed_changelog: dict, old: str, new: str) -> list[str]:
    """Changelog version keys strictly above old and up to new."""
    from packaging.version import InvalidVersion, Version

    out = []
    try:
        ov, nv = Version(old), Version(new)
    except InvalidVersion:
        return list(parsed_changelog.keys())
    for ver in parsed_changelog:
        try:
            v = Version(ver)
        except InvalidVersion:
            continue
        if ov < v <= nv:
            out.append(ver)
    return out


def _changelog_deltas(pkg: str, old: str, new: str, insecure: bool) -> dict:
    """Fetch the package changelog and extract Added/Deprecated/Removed in (old, new]."""
    result = {"changelog_url": None, "added": [], "deprecated": [], "removed": [], "changed": []}
    if not (_get_dependency_changelog_url and _fetch_and_parse_changelog):
        return result
    url = _get_dependency_changelog_url(pkg, insecure=insecure)
    result["changelog_url"] = url
    if not url:
        return result
    parsed = _fetch_and_parse_changelog(url, insecure=insecure)
    if not isinstance(parsed, dict) or not parsed:
        return result
    for ver in _versions_in_range(parsed, old, new):
        entry = parsed.get(ver) or {}
        for cat in ("added", "deprecated", "removed", "changed"):
            for item in (entry.get(cat) or []):
                result[cat].append(f"[{ver}] {item}")
    return result


def _dynamic_deprecations(root: Path, import_target: str, timeout: int = 90) -> list[dict]:
    """Import the project under DeprecationWarning capture; keep warnings from OUR tree."""
    code = (
        "import warnings, json, sys\n"
        "warnings.simplefilter('always')\n"
        "rec = []\n"
        "_orig = warnings.showwarning\n"
        "def _hook(message, category, filename, lineno, file=None, line=None):\n"
        "    if issubclass(category, (DeprecationWarning, PendingDeprecationWarning)):\n"
        "        rec.append({'msg': str(message), 'category': category.__name__,"
        " 'file': filename, 'line': lineno})\n"
        "warnings.showwarning = _hook\n"
        "try:\n"
        f"    __import__({import_target!r})\n"
        "except Exception as e:\n"
        "    rec.append({'msg': 'IMPORT-ERROR: '+repr(e), 'category': 'ImportError',"
        " 'file': '', 'line': 0})\n"
        "print('<<<DEPJSON>>>'+json.dumps(rec))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, cwd=str(root),
            timeout=timeout,
        )
        marker = "<<<DEPJSON>>>"
        idx = proc.stdout.rfind(marker)
        if idx < 0:
            return []
        rec = json.loads(proc.stdout[idx + len(marker):])
    except Exception:
        return []
    root_s = str(root)
    # Keep warnings whose call site is in our own source tree — those are fixable.
    return [r for r in rec if r.get("file", "").startswith(root_s) or r.get("category") == "ImportError"]


_WARN_LINE = None  # compiled lazily


def _pytest_deprecations(root: Path, test_path: str, timeout: int = 280) -> list[dict]:
    """Run pytest under DeprecationWarning capture and parse the warnings summary.

    Far higher yield than importing the package: deprecations usually fire during
    test EXECUTION (e.g. a dep's ``'openai:'`` → ``'openai-chat:'`` notice), not at
    import. Returns parsed {file, line, category, msg} records.
    """
    import re

    global _WARN_LINE
    if _WARN_LINE is None:
        _WARN_LINE = re.compile(
            r"^\s*(?P<file>[^\s:]+\.py):(?P<line>\d+):\s*"
            r"(?P<cat>\w*DeprecationWarning):\s*(?P<msg>.+)$"
        )
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-q", "-p", "no:cacheprovider",
             "-W", "always::DeprecationWarning", "--no-header"],
            capture_output=True, text=True, cwd=str(root), timeout=timeout,
        )
        text = proc.stdout + "\n" + proc.stderr
    except Exception as e:  # noqa: BLE001
        return [{"file": "", "line": 0, "category": "RunError", "msg": type(e).__name__}]
    out: list[dict] = []
    seen: set[tuple] = set()
    for ln in text.splitlines():
        m = _WARN_LINE.match(ln)
        if not m:
            continue
        key = (m.group("file"), m.group("line"), m.group("msg")[:80])
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "file": m.group("file"), "line": int(m.group("line")),
            "category": m.group("cat"), "msg": m.group("msg").strip(),
            "in_our_tree": m.group("file").startswith(str(root)),
        })
    return out


def _score_to_grade(score: int) -> str:
    return "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"


def analyze_dependency_migration(
    root_dir: str = ".",
    *,
    levels: tuple[str, ...] = ("major", "minor"),
    run_dynamic: bool = False,
    import_target: str | None = None,
    pytest_path: str | None = None,
    insecure: bool = False,
    max_pkgs: int = 40,
) -> dict:
    root = Path(root_dir).resolve()

    if _get_latest_version is None or _parse_pyproject is None:
        return {"domain": "Dependency Migration", "score": 0, "grade": "F",
                "findings": ["audit helpers unavailable"], "packages": {}}

    # Determine the upgrade set: declared deps whose installed/constraint is behind PyPI.
    pyproject = root / "pyproject.toml"
    deps = _parse_pyproject(pyproject) if pyproject.exists() else {}
    if not deps and (root / "requirements.txt").exists():
        deps = _parse_requirements(root / "requirements.txt")

    dist_map = _dist_to_import_names()
    targets: list[dict] = []
    for pkg, constraint in deps.items():
        info = _get_latest_version(pkg, insecure=insecure)
        if not info or info.get("latest") in (None, "NOT_FOUND", "unknown"):
            continue
        installed = _get_installed_version(pkg)
        current = installed or constraint
        status = _compare_versions(current, info["latest"]) if current != "Any" else "unknown"
        if status in levels:
            targets.append({"pkg": pkg, "old": current, "new": info["latest"], "level": status})
    targets = targets[:max_pkgs]

    # Which top-level import modules do those packages expose?
    mod_to_pkg: dict[str, str] = {}
    for t in targets:
        for mod in dist_map.get(t["pkg"].lower(), [t["pkg"].replace("-", "_")]):
            mod_to_pkg[mod] = t["pkg"]
    used = _imported_symbols(root, set(mod_to_pkg))

    packages: dict[str, dict] = {}
    total_deprecations = total_new = 0
    for t in targets:
        pkg = t["pkg"]
        mods = dist_map.get(pkg.lower(), [pkg.replace("-", "_")])
        our_symbols = sorted({s for m in mods for s in used.get(m, set())})
        deltas = _changelog_deltas(pkg, t["old"], t["new"], insecure)
        # Deprecated/removed entries that mention a symbol we actually use.
        hits = [e for e in (deltas["deprecated"] + deltas["removed"])
                if any(sym and sym in e for sym in our_symbols)]
        total_deprecations += len(hits)
        total_new += len(deltas["added"])
        packages[pkg] = {
            **t,
            "import_modules": mods,
            "our_used_symbols": our_symbols[:30],
            "changelog_url": deltas["changelog_url"],
            "added": deltas["added"][:15],
            "deprecated": deltas["deprecated"][:15],
            "removed": deltas["removed"][:15],
            "deprecations_affecting_us": hits[:15],
        }

    dynamic: list[dict] = []
    if run_dynamic:
        tgt = import_target or _guess_import_target(root)
        if tgt:
            dynamic = _dynamic_deprecations(root, tgt)
    if pytest_path:
        dynamic.extend(_pytest_deprecations(root, pytest_path))

    findings: list[str] = []
    score = 100
    if total_deprecations:
        score -= min(40, total_deprecations * 5)
        findings.append(
            f"{total_deprecations} deprecated/removed API(s) in upgraded packages "
            "intersect symbols our code imports — review for removal"
        )
    _real = [d for d in dynamic if d.get("category") not in ("ImportError", "RunError")]
    dyn_ours = [d for d in _real if d.get("in_our_tree")]
    dyn_dep = [d for d in _real if not d.get("in_our_tree")]
    if dyn_ours:
        score -= min(30, len(dyn_ours) * 5)
        findings.append(f"{len(dyn_ours)} DeprecationWarning(s) triggered from OUR code — fix these")
    if dyn_dep:
        findings.append(
            f"{len(dyn_dep)} DeprecationWarning(s) from dependencies (forward-looking — "
            "review before the next major; e.g. API renames)"
        )
    if total_new:
        findings.append(
            f"{total_new} new feature(s) added across upgraded packages — review for adoption "
            "(see per-package 'added')"
        )
    if not targets:
        findings.append("No upgradable packages at the requested levels — nothing to migrate")

    score = max(0, score)
    return {
        "domain": "Dependency Migration",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": [{
            "criterion": "dependency_migration",
            "points": score,
            "evidence": f"packages={len(targets)} deprecations_affecting_us={total_deprecations} "
            f"new_features={total_new} dynamic_warnings={len(dyn_ours)}",
            "reasoning": "Cross-referenced upgraded-package changelogs (Added/Deprecated/Removed) "
            "against the symbols our code imports, plus optional runtime DeprecationWarnings.",
        }],
        "packages": packages,
        "dynamic_deprecations": dynamic[:30],
    }


def _guess_import_target(root: Path) -> str | None:
    """Best-effort top-level import package for the project."""
    try:
        import tomllib

        with open(root / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        name = data.get("project", {}).get("name", "")
        cand = name.replace("-", "_")
        if (root / cand / "__init__.py").exists():
            return cand
    except Exception:
        pass
    for child in root.iterdir():
        if child.is_dir() and (child / "__init__.py").exists() and child.name not in _SKIP_DIRS:
            return child.name
    return None


def _self_test() -> int:
    import tempfile

    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "pyproject.toml").write_text('[project]\nname = "demo"\ndependencies = []\n')
        (root / "demo").mkdir()
        (root / "demo" / "__init__.py").write_text(
            "import os\nfrom json import dumps\nos.getcwd()\n"
        )
        syms = _imported_symbols(root, {"os", "json"})
        if "getcwd" not in syms.get("os", set()) or "dumps" not in syms.get("json", set()):
            print("FAIL: _imported_symbols", syms)
            ok = False
        if _guess_import_target(root) != "demo":
            print("FAIL: _guess_import_target")
            ok = False
        # range filter
        rng = _versions_in_range({"1.0.0": {}, "1.5.0": {}, "2.0.0": {}}, "1.0.0", "1.5.0")
        if rng != ["1.5.0"]:
            print("FAIL: _versions_in_range", rng)
            ok = False
    print("analyze_dependency_migration self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Dependency migration intelligence (CE-043)")
    p.add_argument("target", nargs="?", default=".", help="Project root")
    p.add_argument("--levels", default="major,minor", help="Comma-separated: major,minor,patch")
    p.add_argument("--run", action="store_true", help="Also run dynamic DeprecationWarning capture (imports the project)")
    p.add_argument("--import-target", help="Top-level module to import for the dynamic scan")
    p.add_argument("--pytest", dest="pytest_path", help="Run pytest at this path under DeprecationWarning capture (highest-yield deprecation signal)")
    p.add_argument("--insecure", action="store_true", help="Disable SSL verification")
    p.add_argument("--self-test", action="store_true", help="Run offline self-test")
    args = p.parse_args()
    if args.self_test:
        raise SystemExit(_self_test())
    res = analyze_dependency_migration(
        args.target,
        levels=tuple(s.strip() for s in args.levels.split(",") if s.strip()),
        run_dynamic=args.run,
        import_target=args.import_target,
        pytest_path=args.pytest_path,
        insecure=args.insecure,
    )
    print(json.dumps(res, indent=2))

#!/usr/bin/env python3
"""FR-002: Dependency audit for code-enhancer skill.

Parses pyproject.toml and requirements.txt, queries PyPI for latest versions,
and produces a scored dependency health report.

CONCEPT:CE-002 — Dependency Health Audit
"""

import json
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from packaging.version import Version, InvalidVersion

    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def _get_latest_version(package_name: str, insecure: bool = False) -> dict | None:
    if not HAS_REQUESTS:
        return None
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        resp = requests.get(url, timeout=10, verify=not insecure)
        if resp.status_code == 200:
            info = resp.json().get("info", {})
            return {
                "latest": info.get("version", "unknown"),
                "summary": info.get("summary", ""),
            }
        if resp.status_code == 404:
            return {"latest": "NOT_FOUND", "summary": ""}
    except requests.exceptions.RequestException:
        pass
    return None


def _parse_version_spec(raw: str) -> str:
    for op in ["==", ">=", "~=", "<=", "!=", ">", "<"]:
        if op in raw:
            return raw.split(op, 1)[1].split(",")[0].strip()
    return "Any"


def _parse_pyproject(path: Path) -> dict[str, str]:
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {}
    deps: dict[str, str] = {}

    def _extract(dep_str: str) -> tuple[str, str]:
        name = (
            dep_str.split("[")[0]
            .split("<")[0]
            .split(">")[0]
            .split("=")[0]
            .split("~")[0]
            .split("!")[0]
            .strip()
        )
        return name, _parse_version_spec(dep_str)

    for d in data.get("project", {}).get("dependencies", []):
        name, ver = _extract(d)
        if name.lower() != "python":
            deps[name] = ver
    for group_deps in data.get("project", {}).get("optional-dependencies", {}).values():
        for d in group_deps:
            name, ver = _extract(d)
            if name.lower() != "python" and not name.startswith("universal-skills"):
                deps[name] = ver
    return deps


def _parse_requirements(path: Path) -> dict[str, str]:
    deps: dict[str, str] = {}
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                name = (
                    line.split("[")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .split("=")[0]
                    .split("~")[0]
                    .strip()
                )
                deps[name] = _parse_version_spec(line)
    except Exception:
        pass
    return deps


def _compare_versions(current_spec: str, latest: str) -> str:
    if not HAS_PACKAGING or current_spec == "Any":
        return "unknown"
    try:
        cur, lat = Version(current_spec), Version(latest)
    except InvalidVersion:
        return "unknown"
    if cur >= lat:
        return "up-to-date"
    if cur.major < lat.major:
        return "major"
    if cur.minor < lat.minor:
        return "minor"
    return "patch"


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _get_installed_version(package_name: str) -> str | None:
    """Get the installed version of a package via importlib.metadata.

    This is critical for accuracy: we must compare the ACTUAL installed
    version against PyPI, NOT the floor constraint from pyproject.toml.

    Example:
        pyproject.toml says ``networkx>=3.0`` (floor constraint)
        installed version is ``3.6.1``
        PyPI latest is ``3.6.1``
        → Result: "up-to-date" (not "minor update 3.0 → 3.6.1")
    """
    try:
        import importlib.metadata as meta

        return meta.version(package_name)
    except Exception:
        # Try common name normalization (underscores ↔ hyphens)
        try:
            import importlib.metadata as meta

            alt_name = package_name.replace("-", "_")
            return meta.version(alt_name)
        except Exception:
            return None


def audit_dependencies(root_dir: str = ".", insecure: bool = False) -> dict:
    root = Path(root_dir).resolve()
    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"

    if pyproject.exists():
        deps = _parse_pyproject(pyproject)
        source = str(pyproject)
    elif requirements.exists():
        deps = _parse_requirements(requirements)
        source = str(requirements)
    else:
        return {
            "domain": "Dependency Audit",
            "score": 0,
            "grade": "F",
            "findings": ["No pyproject.toml or requirements.txt found"],
            "justifications": [],
            "packages": {},
        }

    if not HAS_REQUESTS:
        return {
            "domain": "Dependency Audit",
            "score": 0,
            "grade": "F",
            "findings": [
                "requests not available — pip install 'universal-skills[code-enhancer]'"
            ],
            "justifications": [],
            "packages": {},
        }

    packages: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(_get_latest_version, pkg, insecure): pkg for pkg in deps
        }
        for future in as_completed(futures):
            pkg = futures[future]
            info = future.result()
            if info:
                # ACCURACY FIX: Use installed version, not floor constraint
                installed = _get_installed_version(pkg)
                effective_version = installed if installed else deps[pkg]
                version_source = "installed" if installed else "constraint"

                packages[pkg] = {
                    "current": effective_version,
                    "constraint": deps[pkg],
                    "installed": installed,
                    "latest": info["latest"],
                    "status": _compare_versions(effective_version, info["latest"]),
                    "version_source": version_source,
                    "summary": info["summary"],
                }

    score = 100
    findings: list[str] = []
    major_count = minor_count = patch_count = 0
    not_installed_count = 0

    for pkg, info in packages.items():
        if info["status"] == "major":
            score -= 10
            major_count += 1
            src_label = (
                " (installed)"
                if info["version_source"] == "installed"
                else " (constraint — not installed)"
            )
            findings.append(
                f"MAJOR update: {pkg} {info['current']}{src_label} -> {info['latest']}"
            )
        elif info["status"] == "minor":
            score -= 3
            minor_count += 1
            src_label = (
                " (installed)"
                if info["version_source"] == "installed"
                else " (constraint — not installed)"
            )
            findings.append(
                f"Minor update: {pkg} {info['current']}{src_label} -> {info['latest']}"
            )
        elif info["status"] == "patch":
            score -= 1
            patch_count += 1
        elif info["latest"] == "NOT_FOUND":
            findings.append(f"Package not found on PyPI: {pkg}")

        if info["version_source"] == "constraint":
            not_installed_count += 1

    # NOTE: Changelog validation moved to audit_changelog.py (CE-023).
    # The old `changelogs` (pyupio) integration was removed — it uses the
    # deprecated `imp` module and is broken on Python 3.12+.

    score = max(0, score)
    justifications = [
        {
            "criterion": "dependency_freshness",
            "points": score,
            "evidence": f"source={source} total={len(deps)} major={major_count} minor={minor_count} patch={patch_count} not_installed={not_installed_count}",
            "reasoning": f"Audited {len(deps)} deps ({len(deps) - not_installed_count} installed, {not_installed_count} constraint-only). "
            f"{major_count} major, {minor_count} minor, {patch_count} patch updates.",
        }
    ]

    return {
        "domain": "Dependency Audit",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "packages": packages,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audit dependencies against PyPI")
    parser.add_argument("target", nargs="?", default=".", help="Project root")
    parser.add_argument(
        "--insecure", action="store_true", help="Disable SSL verification"
    )
    args = parser.parse_args()
    print(json.dumps(audit_dependencies(args.target, insecure=args.insecure), indent=2))

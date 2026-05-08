#!/usr/bin/env python3
"""CE-023: Changelog audit for code-enhancer skill.

Validates the project's own CHANGELOG.md against Keep a Changelog standard,
checks version drift against pyproject.toml, and analyzes dependency changelogs
for version deltas (new features, breaking changes, deprecations).

Replaces the broken `changelogs` (pyupio) integration — that package uses the
removed `imp` module and is incompatible with Python 3.12+.

CONCEPT:CE-023 — Changelog Audit
"""

import json
import tomllib
from datetime import datetime, timezone
from pathlib import Path

try:
    import keepachangelog

    HAS_KEEPACHANGELOG = True
except ImportError:
    HAS_KEEPACHANGELOG = False

try:
    from packaging.version import InvalidVersion, Version

    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Standard Keep a Changelog categories
VALID_CATEGORIES = {"added", "changed", "deprecated", "removed", "fixed", "security"}


def _get_pyproject_version(root: Path) -> str | None:
    """Extract version from pyproject.toml."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version")
    except Exception:
        return None


def _validate_changelog_format(changelog_path: Path) -> dict:
    """Validate CHANGELOG.md against Keep a Changelog 1.1.0 standard."""
    result = {
        "exists": False,
        "parseable": False,
        "has_unreleased": False,
        "version_count": 0,
        "uses_semver": True,
        "valid_categories": True,
        "has_dates": True,
        "has_header": False,
        "issues": [],
    }

    if not changelog_path.exists():
        result["issues"].append("CHANGELOG.md is missing")
        return result

    result["exists"] = True
    content = changelog_path.read_text(encoding="utf-8", errors="ignore")

    # Check header
    if content.strip().startswith("# Changelog") or content.strip().startswith(
        "# CHANGELOG"
    ):
        result["has_header"] = True
    else:
        result["issues"].append("CHANGELOG.md should start with '# Changelog' header")

    # Check for Keep a Changelog reference
    if (
        "keepachangelog.com" not in content
        and "keep a changelog" not in content.lower()
    ):
        result["issues"].append("Missing reference to Keep a Changelog format standard")

    # Try parsing with keepachangelog
    if HAS_KEEPACHANGELOG:
        try:
            data = keepachangelog.to_dict(str(changelog_path))
            result["parseable"] = True
            result["version_count"] = len(data)

            # Check for Unreleased section
            if "unreleased" in {k.lower() for k in data}:
                result["has_unreleased"] = True
            else:
                # Also check raw content for [Unreleased] header
                if "## [Unreleased]" in content:
                    result["has_unreleased"] = True
                else:
                    result["issues"].append(
                        "Missing [Unreleased] section for tracking upcoming changes"
                    )

            # Validate versions
            for version_key, version_data in data.items():
                if version_key.lower() == "unreleased":
                    continue

                # Check semver
                if HAS_PACKAGING:
                    try:
                        Version(version_key)
                    except InvalidVersion:
                        result["uses_semver"] = False
                        result["issues"].append(
                            f"Version '{version_key}' is not valid semver"
                        )

                # Check date
                metadata = version_data.get("metadata", {})
                release_date = metadata.get("release_date")
                if not release_date:
                    result["has_dates"] = False
                    result["issues"].append(
                        f"Version {version_key} is missing a release date"
                    )

                # Check categories
                for cat in version_data:
                    if cat == "metadata":
                        continue
                    if cat.lower() not in VALID_CATEGORIES:
                        result["valid_categories"] = False
                        result["issues"].append(
                            f"Non-standard category '{cat}' in version {version_key}"
                        )

        except Exception as e:
            result["issues"].append(f"Failed to parse CHANGELOG.md: {e}")
    else:
        result["issues"].append(
            "keepachangelog not installed — pip install 'universal-skills[code-enhancer]'"
        )

    return result


def _check_version_drift(changelog_path: Path, pyproject_version: str | None) -> dict:
    """Check if latest changelog version matches pyproject.toml version."""
    drift = {
        "has_drift": False,
        "changelog_version": None,
        "pyproject_version": pyproject_version,
    }

    if not pyproject_version or not HAS_KEEPACHANGELOG:
        return drift

    if not changelog_path.exists():
        drift["has_drift"] = True
        return drift

    try:
        data = keepachangelog.to_dict(str(changelog_path))
        versions = [k for k in data if k.lower() != "unreleased"]
        if versions and HAS_PACKAGING:
            latest_changelog = max(versions, key=lambda v: Version(v))
            drift["changelog_version"] = latest_changelog
            if latest_changelog != pyproject_version:
                drift["has_drift"] = True
    except Exception:
        pass

    return drift


def _get_dependency_changelog_url(
    package_name: str, insecure: bool = False
) -> str | None:
    """Look up a package's changelog URL from PyPI metadata."""
    if not HAS_REQUESTS:
        return None
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        resp = requests.get(url, timeout=10, verify=not insecure)
        if resp.status_code == 200:
            info = resp.json().get("info", {})
            project_urls = info.get("project_urls") or {}
            # Look for changelog-like URL keys
            for key in [
                "Changelog",
                "Changes",
                "History",
                "Release Notes",
                "changelog",
            ]:
                if key in project_urls:
                    return project_urls[key]
            # Fallback: check project_url variants
            for key, val in project_urls.items():
                if "changelog" in key.lower() or "changes" in key.lower():
                    return val
    except Exception:
        pass
    return None


def _fetch_and_parse_changelog(
    changelog_url: str, insecure: bool = False
) -> dict | None:
    """Fetch a remote changelog and try to parse it."""
    if not HAS_REQUESTS:
        return None

    # Convert GitHub blob URLs to raw URLs
    raw_url = changelog_url
    if "github.com" in raw_url and "/blob/" in raw_url:
        raw_url = raw_url.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/", "/"
        )

    try:
        resp = requests.get(raw_url, timeout=15, verify=not insecure)
        if resp.status_code != 200:
            return None

        content = resp.text
        if not content.strip():
            return None

        # Try parsing with keepachangelog by writing to temp
        if HAS_KEEPACHANGELOG:
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(content)
                f.flush()
                try:
                    data = keepachangelog.to_dict(f.name)
                    return data
                except Exception:
                    pass
                finally:
                    Path(f.name).unlink(missing_ok=True)
    except Exception:
        pass

    return None


def _get_changelog_delta(
    changelog_data: dict, from_version: str, to_version: str
) -> dict:
    """Extract changelog entries between two versions (exclusive of from_version)."""
    delta = {
        "versions": [],
        "summary": {
            "added": [],
            "changed": [],
            "deprecated": [],
            "removed": [],
            "fixed": [],
            "security": [],
        },
    }

    if not HAS_PACKAGING or not changelog_data:
        return delta

    try:
        from_v = Version(from_version)
        to_v = Version(to_version)
    except InvalidVersion:
        return delta

    for version_key, version_data in changelog_data.items():
        if version_key.lower() == "unreleased":
            continue
        try:
            v = Version(version_key)
        except InvalidVersion:
            continue

        if from_v < v <= to_v:
            delta["versions"].append(version_key)
            for category in VALID_CATEGORIES:
                items = version_data.get(category, [])
                if items:
                    delta["summary"][category].extend(items)

    delta["versions"].sort(key=lambda x: Version(x))
    return delta


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


def audit_changelog(
    root_dir: str = ".",
    dependency_info: dict | None = None,
    insecure: bool = False,
) -> dict:
    """Audit project changelog and optionally analyze dependency changelogs.

    Args:
        root_dir: Project root directory.
        dependency_info: Optional dict of {package_name: {"current": "x.y.z", "latest": "a.b.c"}}.
        insecure: Disable SSL verification for HTTP requests.

    Returns:
        dict with domain, score, grade, findings, and detailed results.
    """
    root = Path(root_dir).resolve()
    changelog_path = root / "CHANGELOG.md"
    findings: list[str] = []
    score = 100

    # --- Own-repo CHANGELOG validation ---
    format_result = _validate_changelog_format(changelog_path)

    if not format_result["exists"]:
        score -= 25
        findings.append(
            "CHANGELOG.md is missing — create one following Keep a Changelog format"
        )
    elif not format_result["parseable"]:
        score -= 20
        findings.append(
            "CHANGELOG.md exists but could not be parsed — check format compliance"
        )
    else:
        if not format_result["has_header"]:
            score -= 3
        if not format_result["has_unreleased"]:
            score -= 5
            findings.append("CHANGELOG.md missing [Unreleased] section")
        if not format_result["uses_semver"]:
            score -= 5
            findings.append("Some version entries don't follow semver")
        if not format_result["valid_categories"]:
            score -= 3
        if not format_result["has_dates"]:
            score -= 3
        if format_result["version_count"] == 0:
            score -= 10
            findings.append("CHANGELOG.md has no version entries")

    # Version drift check
    pyproject_version = _get_pyproject_version(root)
    drift = _check_version_drift(changelog_path, pyproject_version)
    if drift["has_drift"]:
        score -= 10
        findings.append(
            f"Version drift: pyproject.toml={drift['pyproject_version']} "
            f"vs CHANGELOG.md={drift['changelog_version'] or 'N/A'}"
        )

    # Recency check (if parseable)
    recency_ok = False
    if format_result["parseable"] and HAS_KEEPACHANGELOG:
        try:
            data = keepachangelog.to_dict(str(changelog_path))
            for version_key, version_data in data.items():
                if version_key.lower() == "unreleased":
                    continue
                metadata = version_data.get("metadata", {})
                release_date = metadata.get("release_date")
                if release_date:
                    try:
                        dt = datetime.strptime(release_date, "%Y-%m-%d").replace(
                            tzinfo=timezone.utc
                        )
                        days_ago = (datetime.now(timezone.utc) - dt).days
                        if days_ago <= 30:
                            recency_ok = True
                        break  # Only check most recent
                    except ValueError:
                        pass
        except Exception:
            pass

    if not recency_ok and format_result["exists"]:
        score -= 5
        findings.append("No changelog entries within the last 30 days")

    # --- Dependency changelog analysis ---
    dep_deltas: dict[str, dict] = {}
    if dependency_info and HAS_REQUESTS:
        for pkg, info in dependency_info.items():
            current = info.get("current", "")
            latest = info.get("latest", "")
            status = info.get("status", "")

            if status not in ("major", "minor"):
                continue

            changelog_url = _get_dependency_changelog_url(pkg, insecure)
            if not changelog_url:
                continue

            changelog_data = _fetch_and_parse_changelog(changelog_url, insecure)
            if not changelog_data:
                continue

            delta = _get_changelog_delta(changelog_data, current, latest)
            if delta["versions"]:
                dep_deltas[pkg] = {
                    "from": current,
                    "to": latest,
                    "changelog_url": changelog_url,
                    "versions_changed": len(delta["versions"]),
                    "added_count": len(delta["summary"]["added"]),
                    "changed_count": len(delta["summary"]["changed"]),
                    "deprecated_count": len(delta["summary"]["deprecated"]),
                    "removed_count": len(delta["summary"]["removed"]),
                    "fixed_count": len(delta["summary"]["fixed"]),
                    "security_count": len(delta["summary"]["security"]),
                    "highlights": {k: v[:5] for k, v in delta["summary"].items() if v},
                }

                # Summarize important changes
                if delta["summary"]["security"]:
                    findings.append(
                        f"⚠️ {pkg} has {len(delta['summary']['security'])} "
                        f"security fixes between {current} → {latest}"
                    )
                if delta["summary"]["deprecated"]:
                    findings.append(
                        f"⚠️ {pkg} has {len(delta['summary']['deprecated'])} "
                        f"deprecations between {current} → {latest}"
                    )
                if delta["summary"]["removed"]:
                    findings.append(
                        f"🔴 {pkg} has {len(delta['summary']['removed'])} "
                        f"breaking removals between {current} → {latest}"
                    )
                if delta["summary"]["added"]:
                    findings.append(
                        f"🟢 {pkg} has {len(delta['summary']['added'])} "
                        f"new features between {current} → {latest}"
                    )

    score = max(0, score)

    # Add format issues as findings
    for issue in format_result.get("issues", []):
        if issue not in findings:
            findings.append(issue)

    justifications = [
        {
            "criterion": "changelog_quality",
            "points": score,
            "evidence": json.dumps(
                {
                    "exists": format_result["exists"],
                    "parseable": format_result["parseable"],
                    "version_count": format_result["version_count"],
                    "has_drift": drift["has_drift"],
                    "dep_deltas_found": len(dep_deltas),
                }
            ),
            "reasoning": (
                f"CHANGELOG.md {'exists' if format_result['exists'] else 'missing'}. "
                f"{format_result['version_count']} versions tracked. "
                f"{'Version drift detected. ' if drift['has_drift'] else ''}"
                f"{len(dep_deltas)} dependency changelogs analyzed."
            ),
        }
    ]

    return {
        "domain": "Changelog Audit",
        "score": score,
        "grade": _score_to_grade(score),
        "findings": findings,
        "justifications": justifications,
        "format_validation": format_result,
        "version_drift": drift,
        "dependency_deltas": dep_deltas,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audit project changelog")
    parser.add_argument("target", nargs="?", default=".", help="Project root")
    parser.add_argument(
        "--insecure", action="store_true", help="Disable SSL verification"
    )
    args = parser.parse_args()
    print(json.dumps(audit_changelog(args.target, insecure=args.insecure), indent=2))

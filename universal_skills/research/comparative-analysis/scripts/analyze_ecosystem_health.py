#!/usr/bin/env python3
"""CA-002: Ecosystem health — Git activity, releases, CI, dependency freshness.

Usage: python analyze_ecosystem_health.py /path/to/project

CONCEPT:CA-002 — Repository & Ecosystem Health
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def analyze_git_activity(project_path: Path) -> dict:
    """Analyze git commit frequency, recency, and velocity."""
    try:
        # Last commit date
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else None

        # Commit count last 90 days
        result = subprocess.run(
            ["git", "rev-list", "--count", "--since=90.days", "HEAD"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        commits_90d = int(result.stdout.strip()) if result.returncode == 0 else 0

        # Total commit count
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        total_commits = int(result.stdout.strip()) if result.returncode == 0 else 0

        # Days since last commit
        days_since = None
        if last_commit:
            try:
                dt = datetime.fromisoformat(
                    last_commit.replace(" ", "T").rsplit("+", 1)[0].rsplit("-", 1)[0]
                )
                days_since = (datetime.now() - dt).days
            except Exception:
                pass

        return {
            "last_commit": last_commit,
            "days_since_last_commit": days_since,
            "commits_last_90_days": commits_90d,
            "total_commits": total_commits,
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"error": "git not available"}


def analyze_releases(project_path: Path) -> dict:
    """Analyze release tags for SemVer adherence."""
    try:
        result = subprocess.run(
            ["git", "tag", "--sort=-creatordate"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"count": 0}
        tags = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        semver_pattern = re.compile(r"^v?\d+\.\d+\.\d+")
        semver_tags = [t for t in tags if semver_pattern.match(t)]
        return {
            "total_tags": len(tags),
            "semver_tags": len(semver_tags),
            "semver_compliance": round(len(semver_tags) / max(len(tags), 1) * 100, 1),
            "latest_tag": tags[0] if tags else None,
            "recent_tags": tags[:5],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"count": 0, "error": "git not available"}


def detect_ci(project_path: Path) -> dict:
    """Detect CI/CD configuration."""
    ci_systems = {
        "github_actions": (project_path / ".github" / "workflows").is_dir(),
        "gitlab_ci": (project_path / ".gitlab-ci.yml").exists(),
        "jenkins": (project_path / "Jenkinsfile").exists(),
        "circleci": (project_path / ".circleci" / "config.yml").exists(),
        "travis": (project_path / ".travis.yml").exists(),
        "azure_pipelines": (project_path / "azure-pipelines.yml").exists(),
    }
    workflow_count = 0
    if ci_systems["github_actions"]:
        workflow_count = len(
            list((project_path / ".github" / "workflows").glob("*.yml"))
        )
    return {
        "ci_detected": any(ci_systems.values()),
        "systems": {k: v for k, v in ci_systems.items() if v},
        "workflow_count": workflow_count,
    }


def analyze_dependency_freshness(project_path: Path) -> dict:
    """Basic dependency analysis — count and pinning."""
    dep_info = {"total": 0, "pinned": 0, "unpinned": 0}

    # Python
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib

            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
            deps = data.get("project", {}).get("dependencies", [])
            dep_info["total"] = len(deps)
            for d in deps:
                if "==" in d:
                    dep_info["pinned"] += 1
                else:
                    dep_info["unpinned"] += 1
        except Exception:
            pass

    # Node
    pkg = project_path / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = data.get("dependencies", {})
            dep_info["total"] = len(deps)
            for _, ver in deps.items():
                if ver.startswith("^") or ver.startswith("~"):
                    dep_info["unpinned"] += 1
                else:
                    dep_info["pinned"] += 1
        except Exception:
            pass

    dep_info["pin_rate"] = round(
        dep_info["pinned"] / max(dep_info["total"], 1) * 100, 1
    )
    return dep_info


def score_ecosystem(git: dict, releases: dict, ci: dict, deps: dict) -> dict:
    """Calculate 0-100 ecosystem health score."""
    score = 0
    details = []

    # Git activity (35 points)
    days = git.get("days_since_last_commit")
    if days is not None:
        if days <= 7:
            score += 20
            details.append(f"Active (last commit {days}d ago): +20")
        elif days <= 30:
            score += 15
            details.append(f"Recent activity ({days}d ago): +15")
        elif days <= 90:
            score += 10
            details.append(f"Moderate activity ({days}d ago): +10")
        elif days <= 365:
            score += 5
            details.append(f"Stale ({days}d ago): +5")
        else:
            details.append(f"Dormant ({days}d ago): +0")

    c90 = git.get("commits_last_90_days", 0)
    if c90 >= 50:
        score += 15
        details.append(f"High velocity ({c90} commits/90d): +15")
    elif c90 >= 20:
        score += 10
        details.append(f"Moderate velocity ({c90} commits/90d): +10")
    elif c90 >= 5:
        score += 5
        details.append(f"Low velocity ({c90} commits/90d): +5")

    # Releases (25 points)
    if releases.get("total_tags", 0) >= 5:
        score += 10
        details.append(f"Multiple releases ({releases['total_tags']} tags): +10")
    elif releases.get("total_tags", 0) >= 1:
        score += 5
        details.append(f"Has releases ({releases['total_tags']} tags): +5")

    semver = releases.get("semver_compliance", 0)
    if semver >= 80:
        score += 15
        details.append(f"Strong SemVer compliance ({semver}%): +15")
    elif semver >= 50:
        score += 10
        details.append(f"Partial SemVer ({semver}%): +10")

    # CI (20 points)
    if ci.get("ci_detected"):
        score += 15
        details.append(
            f"CI configured ({', '.join(ci.get('systems', {}).keys())}): +15"
        )
        if ci.get("workflow_count", 0) >= 3:
            score += 5
            details.append(f"Multiple workflows ({ci['workflow_count']}): +5")

    # Dependencies (20 points)
    if deps.get("total", 0) > 0:
        pin_rate = deps.get("pin_rate", 0)
        if pin_rate >= 80:
            score += 20
            details.append(f"Well-pinned deps ({pin_rate}%): +20")
        elif pin_rate >= 50:
            score += 10
            details.append(f"Partially pinned ({pin_rate}%): +10")
        else:
            score += 5
            details.append(f"Mostly unpinned ({pin_rate}%): +5")

    grade = (
        "A+"
        if score >= 95
        else "A"
        if score >= 90
        else "B+"
        if score >= 85
        else "B"
        if score >= 80
        else "C+"
        if score >= 75
        else "C"
        if score >= 70
        else "D"
        if score >= 60
        else "F"
    )
    return {"score": min(score, 100), "grade": grade, "details": details}


def main():
    if len(sys.argv) < 2:
        print(
            json.dumps({"error": "Usage: analyze_ecosystem_health.py <project_path>"})
        )
        sys.exit(1)
    project_path = Path(sys.argv[1]).resolve()
    git = analyze_git_activity(project_path)
    releases = analyze_releases(project_path)
    ci = detect_ci(project_path)
    deps = analyze_dependency_freshness(project_path)
    scoring = score_ecosystem(git, releases, ci, deps)

    print(
        json.dumps(
            {
                "domain": "CA-002",
                "domain_name": "Ecosystem Health",
                "project": str(project_path),
                "git_activity": git,
                "releases": releases,
                "ci": ci,
                "dependencies": deps,
                "scoring": scoring,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
